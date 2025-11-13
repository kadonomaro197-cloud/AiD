# Persona/routine_learning.py
"""
Routine Learning System
Learns user's daily and weekly patterns.
"""

from datetime import datetime, time
from typing import Dict, List
from collections import defaultdict
import json

class RoutineTracker:
    """Tracks and learns user activity patterns."""
    
    def __init__(self):
        # Hour of day activity (0-23)
        self.activity_by_hour = defaultdict(int)
        
        # Day of week activity (0=Monday, 6=Sunday)
        self.activity_by_day = defaultdict(int)
        
        # Hour by day of week (e.g., Monday 9am)
        self.activity_by_hour_and_day = defaultdict(lambda: defaultdict(int))
        
        self.first_activity = None
        self.last_activity = None
        
        self.load_routines()
    
    def log_activity(self, activity_type: str = "message"):
        """Log user activity with timestamp."""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Track activity
        self.activity_by_hour[hour] += 1
        self.activity_by_day[day_of_week] += 1
        self.activity_by_hour_and_day[day_of_week][hour] += 1
        
        # Update timestamps
        if self.first_activity is None:
            self.first_activity = now.isoformat()
        self.last_activity = now.isoformat()
        
        self.save_routines()
    
    def get_active_hours(self, n: int = 8) -> List[int]:
        """Get N most active hours."""
        if not self.activity_by_hour:
            return list(range(9, 17))  # Default: 9am-5pm
        
        sorted_hours = sorted(self.activity_by_hour.items(), 
                            key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:n]]
    
    def get_sleep_hours(self) -> tuple:
        """Estimate likely sleep hours (start, end)."""
        active_hours = self.get_active_hours(12)
        
        # Find biggest gap in active hours
        sorted_active = sorted(active_hours)
        gaps = []
        
        for i in range(len(sorted_active) - 1):
            gap_size = sorted_active[i+1] - sorted_active[i]
            if gap_size > 1:
                gaps.append((sorted_active[i], sorted_active[i+1], gap_size))
        
        if gaps:
            # Biggest gap is likely sleep
            biggest_gap = max(gaps, key=lambda x: x[2])
            sleep_start = biggest_gap[0] + 1
            sleep_end = biggest_gap[1]
            return (sleep_start, sleep_end)
        
        # Default: midnight to 7am
        return (0, 7)
    
    def is_unusual_time(self, check_time: datetime = None) -> bool:
        """Check if current/given time is unusual for user."""
        if check_time is None:
            check_time = datetime.now()
        
        hour = check_time.hour
        day = check_time.weekday()
        
        # Not enough data yet
        if sum(self.activity_by_hour.values()) < 50:
            return False
        
        # Get average activity for this hour
        avg_activity = sum(self.activity_by_hour.values()) / 24
        hour_activity = self.activity_by_hour[hour]
        
        # If this hour has less than 30% of average activity, it's unusual
        return hour_activity < avg_activity * 0.3
    
    def is_likely_sleeping(self, check_time: datetime = None) -> bool:
        """Check if user is likely sleeping."""
        if check_time is None:
            check_time = datetime.now()
        
        sleep_start, sleep_end = self.get_sleep_hours()
        hour = check_time.hour
        
        if sleep_start < sleep_end:
            # Normal case: e.g., 11pm to 7am
            return sleep_start <= hour < sleep_end
        else:
            # Wraps around midnight: e.g., 11pm to 7am
            return hour >= sleep_start or hour < sleep_end
    
    def get_best_checkin_time(self) -> int:
        """Get best hour to check in (most active hour)."""
        active_hours = self.get_active_hours(3)
        if not active_hours:
            return 12  # Default: noon
        
        # Return middle of top 3 most active hours
        return sorted(active_hours)[len(active_hours)//2]
    
    def get_routine_context(self) -> str:
        """Get routine context for system prompt."""
        if sum(self.activity_by_hour.values()) < 20:
            return ""
        
        active_hours = self.get_active_hours(5)
        sleep_start, sleep_end = self.get_sleep_hours()
        now = datetime.now()
        
        context = f"""
**USER ROUTINE PATTERN:**
Active hours: {', '.join([f'{h}:00' for h in sorted(active_hours)])}
Sleep window: {sleep_start}:00 - {sleep_end}:00
Current time: {now.strftime('%H:%M')} ({'usual' if now.hour in active_hours else 'unusual'})
"""
        
        if self.is_likely_sleeping():
            context += "Note: User is likely sleeping right now.\n"
        elif self.is_unusual_time():
            context += "Note: Unusual time for user to be active.\n"
        
        return context
    
    def save_routines(self):
        """Save routine data."""
        try:
            data = {
                "activity_by_hour": dict(self.activity_by_hour),
                "activity_by_day": dict(self.activity_by_day),
                "activity_by_hour_and_day": {
                    str(day): dict(hours) 
                    for day, hours in self.activity_by_hour_and_day.items()
                },
                "first_activity": self.first_activity,
                "last_activity": self.last_activity
            }
            
            with open("Persona/data/routines.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ROUTINES] Error saving: {e}")
    
    def load_routines(self):
        """Load routine data."""
        try:
            with open("Persona/data/routines.json", "r") as f:
                data = json.load(f)
            
            self.activity_by_hour = defaultdict(int, {int(k): v for k, v in data.get("activity_by_hour", {}).items()})
            self.activity_by_day = defaultdict(int, {int(k): v for k, v in data.get("activity_by_day", {}).items()})
            
            hour_day_data = data.get("activity_by_hour_and_day", {})
            self.activity_by_hour_and_day = defaultdict(
                lambda: defaultdict(int),
                {int(day): defaultdict(int, {int(h): c for h, c in hours.items()})
                 for day, hours in hour_day_data.items()}
            )
            
            self.first_activity = data.get("first_activity")
            self.last_activity = data.get("last_activity")
            
        except:
            pass

# =======================
# GLOBAL INSTANCE
# =======================
_routine_tracker = None

def init_routine_tracker():
    """Initialize routine tracking."""
    global _routine_tracker
    _routine_tracker = RoutineTracker()
    print("[ROUTINES] ✓ Routine learning initialized")

def log_activity(activity_type: str = "message"):
    """Log user activity."""
    if _routine_tracker is None:
        init_routine_tracker()
    
    _routine_tracker.log_activity(activity_type)

def get_routine_context() -> str:
    """Get routine context for system prompt."""
    if _routine_tracker:
        return _routine_tracker.get_routine_context()
    return ""

def is_good_time_to_reach_out() -> bool:
    """Check if it's a good time to proactively reach out."""
    if _routine_tracker is None:
        return True
    
    # Don't reach out if likely sleeping
    if _routine_tracker.is_likely_sleeping():
        return False
    
    # Don't reach out during unusual hours
    if _routine_tracker.is_unusual_time():
        return False
    
    return True

def get_tracker():
    """Get tracker instance."""
    return _routine_tracker