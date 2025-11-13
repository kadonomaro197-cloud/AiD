"""
Activity Logger - Phase 4
Comprehensive behavior tracking and analysis
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from collections import defaultdict


class ActivityLogger:
    """
    Logs and analyzes user activity patterns.
    """
    
    def __init__(self, data_dir: str = "Persona/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.activity_file = self.data_dir / "activity_log.json"
        self.activities = []
        self.load_activities()
        
        # Activity categories
        self.categories = {
            'conversation': 'General conversation',
            'coding': 'Programming/development work',
            'worldbuilding': 'Creative worldbuilding',
            'problem_solving': 'Troubleshooting/debugging',
            'planning': 'Planning and organizing',
            'learning': 'Learning new topics',
            'social': 'Social interaction',
            'creative': 'Creative work',
            'maintenance': 'System maintenance'
        }
    
    def log_activity(self, activity_type: str, description: str = "",
                    metadata: Optional[Dict] = None) -> str:
        """
        Log an activity.
        
        Args:
            activity_type: Type of activity (conversation, coding, etc.)
            description: Description of the activity
            metadata: Additional metadata
        
        Returns:
            Activity ID
        """
        import uuid
        
        activity_id = str(uuid.uuid4())
        activity = {
            'id': activity_id,
            'type': activity_type,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.activities.append(activity)
        
        # Auto-save every 10 activities
        if len(self.activities) % 10 == 0:
            self.save_activities()
        
        return activity_id
    
    def log_message(self, message: str, user: str, response: str = ""):
        """Log a message interaction."""
        metadata = {
            'user': user,
            'message_length': len(message),
            'response_length': len(response) if response else 0
        }
        
        # Detect activity type from content
        activity_type = self._detect_activity_type(message)
        
        self.log_activity(
            activity_type=activity_type,
            description=f"{user}: {message[:100]}...",
            metadata=metadata
        )
    
    def _detect_activity_type(self, text: str) -> str:
        """Detect activity type from text content."""
        text_lower = text.lower()
        
        # Check for keywords
        if any(kw in text_lower for kw in ['code', 'function', 'class', 'def', 'error', 'bug']):
            return 'coding'
        elif any(kw in text_lower for kw in ['world', 'character', 'story', 'lore', 'setting']):
            return 'worldbuilding'
        elif any(kw in text_lower for kw in ['plan', 'schedule', 'organize', 'goal', 'task']):
            return 'planning'
        elif any(kw in text_lower for kw in ['learn', 'understand', 'explain', 'teach', 'how']):
            return 'learning'
        elif any(kw in text_lower for kw in ['fix', 'debug', 'issue', 'problem', 'broken']):
            return 'problem_solving'
        elif any(kw in text_lower for kw in ['draw', 'design', 'create', 'make', 'art']):
            return 'creative'
        else:
            return 'conversation'
    
    def get_recent_activities(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent activities."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            a for a in self.activities
            if datetime.fromisoformat(a['timestamp']) >= cutoff
        ]
        
        return sorted(recent, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_activity_summary(self, days: int = 7) -> Dict:
        """Get activity summary for time period."""
        cutoff = datetime.now() - timedelta(days=days)
        
        relevant = [
            a for a in self.activities
            if datetime.fromisoformat(a['timestamp']) >= cutoff
        ]
        
        # Count by type
        type_counts = defaultdict(int)
        for activity in relevant:
            type_counts[activity['type']] += 1
        
        # Calculate daily average
        daily_avg = len(relevant) / days if days > 0 else 0
        
        # Find most active hours
        hour_counts = defaultdict(int)
        for activity in relevant:
            hour = datetime.fromisoformat(activity['timestamp']).hour
            hour_counts[hour] += 1
        
        most_active_hour = max(hour_counts, key=hour_counts.get) if hour_counts else None
        
        return {
            'total_activities': len(relevant),
            'daily_average': round(daily_avg, 1),
            'by_type': dict(type_counts),
            'most_active_hour': most_active_hour,
            'timeframe_days': days
        }
    
    def get_activity_patterns(self, days: int = 30) -> Dict:
        """Analyze activity patterns over time."""
        cutoff = datetime.now() - timedelta(days=days)
        
        relevant = [
            a for a in self.activities
            if datetime.fromisoformat(a['timestamp']) >= cutoff
        ]
        
        if not relevant:
            return {'pattern': 'No activity data'}
        
        # Analyze by day of week
        day_counts = defaultdict(int)
        for activity in relevant:
            day = datetime.fromisoformat(activity['timestamp']).strftime('%A')
            day_counts[day] += 1
        
        # Analyze by time of day
        time_periods = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
        for activity in relevant:
            hour = datetime.fromisoformat(activity['timestamp']).hour
            if 6 <= hour < 12:
                time_periods['morning'] += 1
            elif 12 <= hour < 18:
                time_periods['afternoon'] += 1
            elif 18 <= hour < 22:
                time_periods['evening'] += 1
            else:
                time_periods['night'] += 1
        
        # Most common activities
        type_counts = defaultdict(int)
        for activity in relevant:
            type_counts[activity['type']] += 1
        
        top_activities = sorted(
            type_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Detect engagement patterns
        pattern_description = self._describe_patterns(
            day_counts, time_periods, top_activities
        )
        
        return {
            'by_day_of_week': dict(day_counts),
            'by_time_period': time_periods,
            'top_activities': top_activities,
            'pattern_description': pattern_description
        }
    
    def _describe_patterns(self, day_counts: Dict, time_periods: Dict, 
                          top_activities: List[Tuple]) -> str:
        """Generate human-readable pattern description."""
        descriptions = []
        
        # Most active day
        if day_counts:
            most_active_day = max(day_counts, key=day_counts.get)
            descriptions.append(f"Most active on {most_active_day}s")
        
        # Preferred time
        if time_periods:
            pref_time = max(time_periods, key=time_periods.get)
            descriptions.append(f"Prefers {pref_time} interactions")
        
        # Main activities
        if top_activities:
            main_activity = top_activities[0][0]
            descriptions.append(f"Primary activity: {main_activity}")
        
        return ". ".join(descriptions) + "."
    
    def get_streak_info(self, activity_type: Optional[str] = None) -> Dict:
        """Calculate current streak of activity."""
        if activity_type:
            relevant = [a for a in self.activities if a['type'] == activity_type]
        else:
            relevant = self.activities
        
        if not relevant:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # Sort by date
        sorted_activities = sorted(
            relevant,
            key=lambda x: datetime.fromisoformat(x['timestamp'])
        )
        
        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        temp_streak = 1
        
        last_date = None
        for activity in sorted_activities:
            activity_date = datetime.fromisoformat(activity['timestamp']).date()
            
            if last_date is None:
                last_date = activity_date
                continue
            
            # Check if consecutive day
            if activity_date == last_date + timedelta(days=1):
                temp_streak += 1
            elif activity_date == last_date:
                # Same day, don't change streak
                pass
            else:
                # Streak broken
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
            
            last_date = activity_date
        
        # Check if current streak is still active
        if last_date == datetime.now().date():
            current_streak = temp_streak
        
        longest_streak = max(longest_streak, temp_streak)
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'activity_type': activity_type or 'all'
        }
    
    def get_daily_report(self) -> str:
        """Generate daily activity report."""
        today_activities = self.get_recent_activities(hours=24)
        
        if not today_activities:
            return "No activities logged today."
        
        # Count by type
        type_counts = defaultdict(int)
        for activity in today_activities:
            type_counts[activity['type']] += 1
        
        report = "📊 **Today's Activity Report**\n\n"
        report += f"**Total Activities:** {len(today_activities)}\n\n"
        
        if type_counts:
            report += "**By Type:**\n"
            for activity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                report += f"  • {activity_type.title()}: {count}\n"
        
        return report
    
    def export_activities(self, days: int = 30, filename: Optional[str] = None) -> str:
        """Export activities to JSON file."""
        cutoff = datetime.now() - timedelta(days=days)
        
        export_data = [
            a for a in self.activities
            if datetime.fromisoformat(a['timestamp']) >= cutoff
        ]
        
        if filename is None:
            filename = f"activity_export_{datetime.now().strftime('%Y%m%d')}.json"
        
        export_path = self.data_dir / filename
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"[ACTIVITY] Exported {len(export_data)} activities to {filename}")
        return str(export_path)
    
    def save_activities(self):
        """Save activities to disk."""
        with open(self.activity_file, 'w', encoding='utf-8') as f:
            json.dump(self.activities, f, indent=2, ensure_ascii=False)
    
    def load_activities(self):
        """Load activities from disk."""
        if self.activity_file.exists():
            try:
                with open(self.activity_file, 'r', encoding='utf-8') as f:
                    self.activities = json.load(f)
                print(f"[ACTIVITY] Loaded {len(self.activities)} activities")
            except Exception as e:
                print(f"[ACTIVITY] Error loading activities: {e}")
                self.activities = []
        else:
            self.activities = []


# =======================
# GLOBAL INSTANCE
# =======================
_logger = None

def get_logger() -> ActivityLogger:
    """Get or create activity logger instance."""
    global _logger
    if _logger is None:
        _logger = ActivityLogger()
    return _logger

def init_activity_logger():
    """Initialize activity logger."""
    get_logger()
    print("[ACTIVITY] Activity logger initialized")

def log_activity(activity_type: str, description: str = "", metadata: Dict = None) -> str:
    """Log an activity."""
    return get_logger().log_activity(activity_type, description, metadata)

def log_message(message: str, user: str, response: str = ""):
    """Log a message interaction."""
    get_logger().log_message(message, user, response)

def get_activity_summary(days: int = 7) -> Dict:
    """Get activity summary."""
    return get_logger().get_activity_summary(days)

def get_daily_report() -> str:
    """Get daily activity report."""
    return get_logger().get_daily_report()

def get_activity_patterns(days: int = 30) -> Dict:
    """Get activity patterns."""
    return get_logger().get_activity_patterns(days)
