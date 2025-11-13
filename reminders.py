"""
Reminders System - Phase 4
Time-based notifications and recurring reminders
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from pathlib import Path
import threading
import time


class ReminderManager:
    """
    Manages time-based reminders and recurring notifications.
    """
    
    def __init__(self, data_dir: str = "Persona/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.reminders_file = self.data_dir / "reminders.json"
        self.reminders = []
        self.load_reminders()
        
        # Threading
        self.running = False
        self.thread = None
        self.reminder_callback = None
    
    def start(self, callback: Callable[[str, Dict], None]):
        """
        Start reminder system.
        
        Args:
            callback: Function(message, reminder_data) to call when reminder triggers
        """
        if self.running:
            return
        
        self.reminder_callback = callback
        self.running = True
        
        self.thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.thread.start()
        
        print("[REMINDERS] Reminder system started")
    
    def stop(self):
        """Stop reminder system."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        self.save_reminders()
        print("[REMINDERS] Reminder system stopped")
    
    def _reminder_loop(self):
        """Main reminder checking loop."""
        while self.running:
            try:
                self._check_reminders()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"[REMINDERS] Error in reminder loop: {e}")
                time.sleep(60)
    
    def _check_reminders(self):
        """Check for due reminders."""
        now = datetime.now()
        triggered = []
        remaining = []
        
        for reminder in self.reminders:
            if reminder['status'] != 'active':
                remaining.append(reminder)
                continue
            
            trigger_time = datetime.fromisoformat(reminder['trigger_time'])
            
            if trigger_time <= now:
                # Trigger reminder
                if self.reminder_callback:
                    self.reminder_callback(reminder['message'], reminder)
                
                # Handle recurring
                if reminder['recurring']:
                    # Schedule next occurrence
                    next_time = self._calculate_next_occurrence(
                        trigger_time,
                        reminder['recurrence_pattern']
                    )
                    reminder['trigger_time'] = next_time.isoformat()
                    reminder['times_triggered'] = reminder.get('times_triggered', 0) + 1
                    remaining.append(reminder)
                    
                    print(f"[REMINDERS] Recurring reminder scheduled for {next_time}")
                else:
                    # Mark as completed
                    reminder['status'] = 'completed'
                    reminder['completed_at'] = now.isoformat()
                    remaining.append(reminder)
                
                triggered.append(reminder)
            else:
                remaining.append(reminder)
        
        if triggered:
            self.reminders = remaining
            self.save_reminders()
    
    def create_reminder(self, message: str, trigger_time: datetime,
                       recurring: bool = False, recurrence_pattern: str = "daily",
                       metadata: Optional[Dict] = None) -> str:
        """
        Create a new reminder.
        
        Args:
            message: Reminder message
            trigger_time: When to trigger
            recurring: Whether it repeats
            recurrence_pattern: "daily", "weekly", "monthly"
            metadata: Additional data
        
        Returns:
            Reminder ID
        """
        import uuid
        
        reminder_id = str(uuid.uuid4())
        
        reminder = {
            'id': reminder_id,
            'message': message,
            'trigger_time': trigger_time.isoformat(),
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'recurring': recurring,
            'recurrence_pattern': recurrence_pattern if recurring else None,
            'times_triggered': 0,
            'metadata': metadata or {}
        }
        
        self.reminders.append(reminder)
        self.save_reminders()
        
        print(f"[REMINDERS] Created reminder for {trigger_time.strftime('%Y-%m-%d %H:%M')}")
        return reminder_id
    
    def _calculate_next_occurrence(self, last_time: datetime, pattern: str) -> datetime:
        """Calculate next occurrence time for recurring reminder."""
        if pattern == "daily":
            return last_time + timedelta(days=1)
        elif pattern == "weekly":
            return last_time + timedelta(weeks=1)
        elif pattern == "monthly":
            # Add 30 days (simplified)
            return last_time + timedelta(days=30)
        elif pattern == "hourly":
            return last_time + timedelta(hours=1)
        else:
            return last_time + timedelta(days=1)
    
    def cancel_reminder(self, reminder_id: str):
        """Cancel a reminder."""
        for reminder in self.reminders:
            if reminder['id'] == reminder_id:
                reminder['status'] = 'cancelled'
                reminder['cancelled_at'] = datetime.now().isoformat()
                self.save_reminders()
                print(f"[REMINDERS] Cancelled reminder: {reminder_id}")
                return True
        
        return False
    
    def get_active_reminders(self) -> List[Dict]:
        """Get all active reminders."""
        return [r for r in self.reminders if r['status'] == 'active']
    
    def get_upcoming_reminders(self, hours: int = 24) -> List[Dict]:
        """Get reminders due in next N hours."""
        cutoff = datetime.now() + timedelta(hours=hours)
        
        upcoming = []
        for reminder in self.reminders:
            if reminder['status'] == 'active':
                trigger_time = datetime.fromisoformat(reminder['trigger_time'])
                if trigger_time <= cutoff:
                    upcoming.append(reminder)
        
        return sorted(upcoming, key=lambda r: r['trigger_time'])
    
    def get_reminder(self, reminder_id: str) -> Optional[Dict]:
        """Get specific reminder."""
        for reminder in self.reminders:
            if reminder['id'] == reminder_id:
                return reminder
        return None
    
    def list_all_reminders(self) -> str:
        """Get text list of all reminders."""
        active = self.get_active_reminders()
        
        if not active:
            return "No active reminders"
        
        lines = ["**Active Reminders:**\n"]
        for reminder in sorted(active, key=lambda r: r['trigger_time']):
            trigger = datetime.fromisoformat(reminder['trigger_time'])
            time_until = trigger - datetime.now()
            
            hours = time_until.total_seconds() / 3600
            if hours < 1:
                time_str = f"{int(time_until.total_seconds() / 60)} minutes"
            elif hours < 24:
                time_str = f"{int(hours)} hours"
            else:
                time_str = f"{int(hours / 24)} days"
            
            recurring = " (recurring)" if reminder['recurring'] else ""
            lines.append(f"• {reminder['message']} - in {time_str}{recurring}")
        
        return "\n".join(lines)
    
    def save_reminders(self):
        """Save reminders to disk."""
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, indent=2, ensure_ascii=False)
    
    def load_reminders(self):
        """Load reminders from disk."""
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
                
                active = len([r for r in self.reminders if r['status'] == 'active'])
                print(f"[REMINDERS] Loaded {active} active reminders")
            except Exception as e:
                print(f"[REMINDERS] Error loading reminders: {e}")
                self.reminders = []


# =======================
# GLOBAL INSTANCE
# =======================
_reminder_manager = None

def get_reminder_manager() -> ReminderManager:
    """Get or create reminder manager instance."""
    global _reminder_manager
    if _reminder_manager is None:
        _reminder_manager = ReminderManager()
    return _reminder_manager

def init_reminders(callback: Callable[[str, Dict], None] = None):
    """Initialize reminder system."""
    manager = get_reminder_manager()
    if callback:
        manager.start(callback)
    print("[REMINDERS] Reminder system initialized")

def create_reminder(message: str, trigger_time: datetime, **kwargs) -> str:
    """Create a reminder."""
    return get_reminder_manager().create_reminder(message, trigger_time, **kwargs)

def cancel_reminder(reminder_id: str) -> bool:
    """Cancel a reminder."""
    return get_reminder_manager().cancel_reminder(reminder_id)

def get_upcoming_reminders(hours: int = 24) -> List[Dict]:
    """Get upcoming reminders."""
    return get_reminder_manager().get_upcoming_reminders(hours)

def list_reminders() -> str:
    """List all reminders."""
    return get_reminder_manager().list_all_reminders()
