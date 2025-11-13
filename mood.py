"""
Mood Tracking System - Phase 4
Track emotional patterns and provide insights
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from collections import defaultdict


class MoodTracker:
    """
    Tracks emotional patterns over time.
    """
    
    def __init__(self, data_dir: str = "Persona/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.mood_file = self.data_dir / "mood_log.json"
        self.mood_log = []
        self.load_mood_log()
        
        # Emotion categories
        self.emotions = {
            'positive': ['happy', 'excited', 'joyful', 'proud', 'grateful', 'content', 'peaceful', 'hopeful'],
            'negative': ['sad', 'angry', 'frustrated', 'anxious', 'stressed', 'worried', 'disappointed', 'lonely'],
            'neutral': ['calm', 'thoughtful', 'focused', 'tired', 'bored']
        }
        
        # Emotion detection keywords
        self.emotion_keywords = {
            'happy': ['happy', 'joyful', 'glad', 'cheerful', 'delighted'],
            'excited': ['excited', 'pumped', 'thrilled', 'eager', 'enthusiastic'],
            'sad': ['sad', 'down', 'unhappy', 'depressed', 'blue'],
            'angry': ['angry', 'mad', 'furious', 'irritated', 'pissed'],
            'anxious': ['anxious', 'nervous', 'worried', 'uneasy', 'stressed'],
            'frustrated': ['frustrated', 'annoyed', 'bothered', 'aggravated'],
            'proud': ['proud', 'accomplished', 'achieved', 'succeeded'],
            'grateful': ['grateful', 'thankful', 'appreciate', 'blessed'],
            'tired': ['tired', 'exhausted', 'fatigued', 'drained', 'worn out'],
            'stressed': ['stressed', 'overwhelmed', 'pressure', 'burden'],
            'calm': ['calm', 'relaxed', 'peaceful', 'tranquil', 'serene'],
            'lonely': ['lonely', 'alone', 'isolated', 'disconnected']
        }
    
    def detect_emotion(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect emotion from text.
        
        Returns:
            (emotion_name, confidence_score) or (None, 0.0)
        """
        text_lower = text.lower()
        
        # Count matches for each emotion
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if not emotion_scores:
            return None, 0.0
        
        # Return emotion with highest score
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[best_emotion]
        confidence = min(max_score * 0.3, 1.0)  # Scale confidence
        
        return best_emotion, confidence
    
    def log_mood(self, emotion: str, intensity: int = 5, 
                 notes: str = "", auto_detected: bool = False) -> str:
        """
        Log a mood entry.
        
        Args:
            emotion: The emotion name
            intensity: 1-10 scale
            notes: Optional notes about the mood
            auto_detected: Whether this was auto-detected
        
        Returns:
            Entry ID
        """
        import uuid
        
        entry_id = str(uuid.uuid4())
        entry = {
            'id': entry_id,
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion,
            'intensity': max(1, min(10, intensity)),  # Clamp to 1-10
            'notes': notes,
            'auto_detected': auto_detected
        }
        
        self.mood_log.append(entry)
        self.save_mood_log()
        
        if not auto_detected:
            print(f"[MOOD] Logged: {emotion} (intensity: {intensity}/10)")
        
        return entry_id
    
    def analyze_message_mood(self, message: str) -> Optional[str]:
        """
        Analyze message for mood and auto-log if detected.
        
        Returns:
            Entry ID if mood logged, None otherwise
        """
        emotion, confidence = self.detect_emotion(message)
        
        if emotion and confidence >= 0.5:
            # Auto-log with intensity based on confidence
            intensity = int(confidence * 10)
            return self.log_mood(
                emotion=emotion,
                intensity=intensity,
                notes=message[:100],  # Store snippet
                auto_detected=True
            )
        
        return None
    
    def get_recent_moods(self, hours: int = 24) -> List[Dict]:
        """Get moods from last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []
        
        for entry in self.mood_log:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            if timestamp >= cutoff:
                recent.append(entry)
        
        return sorted(recent, key=lambda x: x['timestamp'], reverse=True)
    
    def get_mood_trend(self, days: int = 7) -> Dict:
        """
        Analyze mood trend over last N days.
        
        Returns:
            Dict with trend analysis
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter relevant entries
        relevant = [
            e for e in self.mood_log 
            if datetime.fromisoformat(e['timestamp']) >= cutoff
        ]
        
        if not relevant:
            return {
                'trend': 'neutral',
                'average_intensity': 0,
                'dominant_emotions': [],
                'pattern': 'No data available'
            }
        
        # Calculate average intensity
        avg_intensity = sum(e['intensity'] for e in relevant) / len(relevant)
        
        # Count emotions
        emotion_counts = defaultdict(int)
        positive_count = 0
        negative_count = 0
        
        for entry in relevant:
            emotion = entry['emotion']
            emotion_counts[emotion] += 1
            
            # Classify as positive/negative
            if emotion in self.emotions['positive']:
                positive_count += 1
            elif emotion in self.emotions['negative']:
                negative_count += 1
        
        # Determine trend
        if positive_count > negative_count * 1.5:
            trend = 'improving'
        elif negative_count > positive_count * 1.5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Get dominant emotions
        top_emotions = sorted(
            emotion_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Generate pattern description
        pattern = self._describe_pattern(relevant, trend, avg_intensity)
        
        return {
            'trend': trend,
            'average_intensity': round(avg_intensity, 1),
            'dominant_emotions': [e for e, _ in top_emotions],
            'emotion_counts': dict(emotion_counts),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'total_entries': len(relevant),
            'pattern': pattern
        }
    
    def _describe_pattern(self, entries: List[Dict], trend: str, avg_intensity: float) -> str:
        """Generate human-readable pattern description."""
        if not entries:
            return "No mood data available"
        
        descriptions = []
        
        # Trend description
        if trend == 'improving':
            descriptions.append("Mood has been improving")
        elif trend == 'declining':
            descriptions.append("Mood has been declining")
        else:
            descriptions.append("Mood has been stable")
        
        # Intensity description
        if avg_intensity >= 7:
            descriptions.append("with strong emotional intensity")
        elif avg_intensity >= 5:
            descriptions.append("with moderate emotional intensity")
        else:
            descriptions.append("with mild emotional intensity")
        
        # Most common emotion
        emotion_counts = defaultdict(int)
        for e in entries:
            emotion_counts[e['emotion']] += 1
        
        if emotion_counts:
            most_common = max(emotion_counts, key=emotion_counts.get)
            descriptions.append(f"Most common emotion: {most_common}")
        
        return ". ".join(descriptions) + "."
    
    def get_emotion_distribution(self, days: int = 30) -> Dict:
        """Get distribution of emotions over time period."""
        cutoff = datetime.now() - timedelta(days=days)
        
        relevant = [
            e for e in self.mood_log 
            if datetime.fromisoformat(e['timestamp']) >= cutoff
        ]
        
        distribution = defaultdict(int)
        for entry in relevant:
            distribution[entry['emotion']] += 1
        
        total = len(relevant)
        percentages = {
            emotion: round((count / total) * 100, 1)
            for emotion, count in distribution.items()
        } if total > 0 else {}
        
        return {
            'counts': dict(distribution),
            'percentages': percentages,
            'total_entries': total
        }
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict:
        """Get mood summary for a specific day."""
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        day_entries = [
            e for e in self.mood_log
            if start_of_day <= datetime.fromisoformat(e['timestamp']) < end_of_day
        ]
        
        if not day_entries:
            return {
                'date': date.strftime('%Y-%m-%d'),
                'entries': 0,
                'summary': 'No mood data for this day'
            }
        
        # Calculate stats
        avg_intensity = sum(e['intensity'] for e in day_entries) / len(day_entries)
        
        emotion_counts = defaultdict(int)
        for e in day_entries:
            emotion_counts[e['emotion']] += 1
        
        dominant = max(emotion_counts, key=emotion_counts.get)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'entries': len(day_entries),
            'average_intensity': round(avg_intensity, 1),
            'dominant_emotion': dominant,
            'all_emotions': dict(emotion_counts),
            'summary': f"{len(day_entries)} mood entries, primarily {dominant}"
        }
    
    def get_weekly_report(self) -> str:
        """Generate a weekly mood report."""
        trend = self.get_mood_trend(days=7)
        
        report = "📊 **Weekly Mood Report**\n\n"
        report += f"**Trend:** {trend['trend'].title()}\n"
        report += f"**Average Intensity:** {trend['average_intensity']}/10\n"
        report += f"**Total Entries:** {trend['total_entries']}\n\n"
        
        if trend['dominant_emotions']:
            report += "**Dominant Emotions:**\n"
            for emotion in trend['dominant_emotions']:
                count = trend['emotion_counts'][emotion]
                report += f"  • {emotion.title()}: {count} times\n"
            report += "\n"
        
        report += f"**Pattern:** {trend['pattern']}\n"
        
        # Add balance indicator
        pos = trend['positive_count']
        neg = trend['negative_count']
        total = pos + neg
        
        if total > 0:
            pos_pct = (pos / total) * 100
            report += f"\n**Emotional Balance:** {pos_pct:.0f}% positive, {100-pos_pct:.0f}% negative\n"
        
        return report
    
    def save_mood_log(self):
        """Save mood log to disk."""
        with open(self.mood_file, 'w', encoding='utf-8') as f:
            json.dump(self.mood_log, f, indent=2, ensure_ascii=False)
    
    def load_mood_log(self):
        """Load mood log from disk."""
        if self.mood_file.exists():
            try:
                with open(self.mood_file, 'r', encoding='utf-8') as f:
                    self.mood_log = json.load(f)
                print(f"[MOOD] Loaded {len(self.mood_log)} mood entries")
            except Exception as e:
                print(f"[MOOD] Error loading mood log: {e}")
                self.mood_log = []
        else:
            self.mood_log = []


# =======================
# GLOBAL INSTANCE
# =======================
_tracker = None

def get_tracker() -> MoodTracker:
    """Get or create mood tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = MoodTracker()
    return _tracker

def init_mood_tracker():
    """Initialize mood tracker."""
    get_tracker()
    print("[MOOD] Mood tracker initialized")

def log_mood(emotion: str, intensity: int = 5, notes: str = "") -> str:
    """Log a mood entry."""
    return get_tracker().log_mood(emotion, intensity, notes)

def analyze_message(message: str) -> Optional[str]:
    """Analyze message for mood."""
    return get_tracker().analyze_message_mood(message)

def get_mood_trend(days: int = 7) -> Dict:
    """Get mood trend."""
    return get_tracker().get_mood_trend(days)

def get_weekly_report() -> str:
    """Get weekly mood report."""
    return get_tracker().get_weekly_report()

def get_daily_summary(date: Optional[datetime] = None) -> Dict:
    """Get daily mood summary."""
    return get_tracker().get_daily_summary(date)
