# Persona/proactive.py
"""
Proactive Engagement System
AiD reaches out first, checks in, follows up naturally.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import threading
import time

# =======================
# FOLLOW-UP TRACKER
# =======================
class FollowUpTracker:
    """Tracks things worth following up on."""
    
    def __init__(self):
        self.pending_followups = []
        self.followup_patterns = {
            # User mentions future action
            "future_action": {
                "triggers": ["i'll", "i'm going to", "gonna", "planning to", "will"],
                "followup_days": 2,
                "question_templates": [
                    "How'd {topic} go?",
                    "Did you get around to {topic}?",
                    "Any progress on {topic}?"
                ]
            },
            # User mentions problem
            "problem": {
                "triggers": ["frustrated", "stuck", "can't figure", "struggling with"],
                "followup_days": 1,
                "question_templates": [
                    "Did you sort out that {topic} issue?",
                    "Any luck with {topic}?",
                    "Still dealing with {topic}?"
                ]
            },
            # User mentions goal
            "goal": {
                "triggers": ["working on", "trying to", "need to finish"],
                "followup_days": 3,
                "question_templates": [
                    "How's {topic} coming along?",
                    "Made any progress on {topic}?",
                    "Still chipping away at {topic}?"
                ]
            },
            # User mentions waiting
            "waiting": {
                "triggers": ["waiting for", "expecting", "should arrive", "coming next"],
                "followup_days": 2,
                "question_templates": [
                    "Did {topic} ever show up?",
                    "Any news on {topic}?",
                    "{topic} sorted yet?"
                ]
            }
        }
    
    def analyze_for_followup(self, message: str, context: str = "") -> Optional[Dict]:
        """Check if message needs follow-up."""
        msg_lower = message.lower()
        
        for pattern_type, pattern_data in self.followup_patterns.items():
            if any(trigger in msg_lower for trigger in pattern_data["triggers"]):
                # Extract topic (simplified - you can improve with NLP)
                words = message.split()
                topic = " ".join(words[:10])  # First 10 words as topic
                
                return {
                    "type": pattern_type,
                    "topic": topic,
                    "original_message": message,
                    "days_until_followup": pattern_data["followup_days"],
                    "created": datetime.now().isoformat(),
                    "due_date": (datetime.now() + timedelta(days=pattern_data["followup_days"])).isoformat()
                }
        
        return None
    
    def schedule_followup(self, followup_data: Dict):
        """Add follow-up to queue."""
        self.pending_followups.append(followup_data)
        self.save_followups()
        
        print(f"[PROACTIVE] Scheduled follow-up on '{followup_data['topic'][:30]}...' in {followup_data['days_until_followup']} days")
    
    def get_due_followups(self) -> List[Dict]:
        """Get follow-ups that are due."""
        now = datetime.now()
        due = []
        
        for followup in self.pending_followups[:]:
            due_date = datetime.fromisoformat(followup["due_date"])
            if now >= due_date:
                due.append(followup)
                self.pending_followups.remove(followup)
        
        if due:
            self.save_followups()
        
        return due
    
    def save_followups(self):
        """Save pending follow-ups."""
        try:
            with open("Persona/data/followups.json", "w") as f:
                json.dump(self.pending_followups, f, indent=2)
        except Exception as e:
            print(f"[PROACTIVE] Error saving followups: {e}")
    
    def load_followups(self):
        """Load pending follow-ups."""
        try:
            with open("Persona/data/followups.json", "r") as f:
                self.pending_followups = json.load(f)
        except:
            self.pending_followups = []

# =======================
# CHECK-IN SYSTEM
# =======================
class CheckInSystem:
    """Manages natural check-ins."""
    
    def __init__(self):
        self.last_interaction = datetime.now()
        self.check_in_intervals = {
            "short": 4,    # hours - for ongoing conversations
            "medium": 12,  # hours - daily check
            "long": 24,    # hours - if quiet for a day
            "extended": 48 # hours - if really quiet
        }
        
        self.check_in_templates = {
            "short": [
                "Oi, you alright? Bit quiet innit.",
                "Still there, boss?",
                "Everything sorted?"
            ],
            "medium": [
                "How's it goin', mate?",
                "What you been up to?",
                "Alright? How's the day treatin' ya?"
            ],
            "long": [
                "Oi, haven't heard from ya in a bit. Everything alright?",
                "Been a while, boss. What's happening?",
                "You good? Bit quiet on your end."
            ],
            "extended": [
                "Right, now I'm proper worried. You alright, mate?",
                "Boss? Where'd you disappear to?",
                "Oi, it's been two days. Just checkin' you're still kickin'."
            ]
        }
    
    def update_last_interaction(self):
        """User interacted - reset timer."""
        self.last_interaction = datetime.now()
        self.save_state()
    
    def should_check_in(self) -> Optional[str]:
        """Determine if should check in and what type."""
        hours_since = (datetime.now() - self.last_interaction).total_seconds() / 3600
        
        if hours_since >= self.check_in_intervals["extended"]:
            return "extended"
        elif hours_since >= self.check_in_intervals["long"]:
            return "long"
        elif hours_since >= self.check_in_intervals["medium"]:
            return "medium"
        elif hours_since >= self.check_in_intervals["short"]:
            return "short"
        
        return None
    
    def save_state(self):
        """Save check-in state."""
        try:
            with open("Persona/data/checkin_state.json", "w") as f:
                json.dump({
                    "last_interaction": self.last_interaction.isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"[PROACTIVE] Error saving check-in state: {e}")
    
    def load_state(self):
        """Load check-in state."""
        try:
            with open("Persona/data/checkin_state.json", "r") as f:
                data = json.load(f)
                self.last_interaction = datetime.fromisoformat(data["last_interaction"])
        except:
            self.last_interaction = datetime.now()

# =======================
# PROACTIVE ENGINE
# =======================
class ProactiveEngine:
    """Main proactive engagement coordinator."""
    
    def __init__(self):
        self.followup_tracker = FollowUpTracker()
        self.checkin_system = CheckInSystem()
        self.active = False
        self.monitor_thread = None
        
        # Load existing state
        self.followup_tracker.load_followups()
        self.checkin_system.load_state()
    
    def start(self):
        """Start proactive monitoring."""
        self.active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("[PROACTIVE] Proactive engagement system started")
    
    def stop(self):
        """Stop proactive monitoring."""
        self.active = False
        print("[PROACTIVE] Proactive engagement system stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop - checks every 5 minutes."""
        while self.active:
            try:
                # Check for due follow-ups
                due_followups = self.followup_tracker.get_due_followups()
                for followup in due_followups:
                    self._trigger_followup(followup)
                
                # Check if should do general check-in
                checkin_type = self.checkin_system.should_check_in()
                if checkin_type:
                    self._trigger_checkin(checkin_type)
                
                time.sleep(300)  # Check every 5 minutes
            
            except Exception as e:
                print(f"[PROACTIVE] Monitor error: {e}")
                time.sleep(300)
    
    def _trigger_followup(self, followup: Dict):
        """Trigger a follow-up message."""
        import random
        
        pattern_data = self.followup_tracker.followup_patterns.get(followup["type"])
        if pattern_data:
            template = random.choice(pattern_data["question_templates"])
            message = template.format(topic=followup["topic"][:50])
            
            print(f"\n[PROACTIVE] 📨 FOLLOW-UP MESSAGE READY:")
            print(f"   {message}")
            print(f"   (Original: {followup['original_message'][:60]}...)\n")
            
            # TODO: Actually send via Discord bot
            # self._send_proactive_message(message)
    
    def _trigger_checkin(self, checkin_type: str):
        """Trigger a check-in message."""
        import random
        
        template = random.choice(self.checkin_system.check_in_templates[checkin_type])
        
        print(f"\n[PROACTIVE] 📨 CHECK-IN MESSAGE READY:")
        print(f"   {template}")
        print(f"   (Type: {checkin_type}, Last interaction: {self.checkin_system.last_interaction})\n")
        
        # Mark as checked in (wait for next interval)
        self.checkin_system.update_last_interaction()
        
        # TODO: Actually send via Discord bot
        # self._send_proactive_message(template)
    
    def process_user_message(self, message: str) -> int:
        """
        Process user message for proactive opportunities.
        Returns: number of follow-ups scheduled.
        """
        # Update interaction time
        self.checkin_system.update_last_interaction()
        
        # Check if message warrants follow-up
        followup = self.followup_tracker.analyze_for_followup(message)
        
        if followup:
            self.followup_tracker.schedule_followup(followup)
            return 1
        
        return 0

# =======================
# GLOBAL INSTANCE
# =======================
_proactive_engine = None

def init_proactive():
    """Initialize proactive system."""
    global _proactive_engine
    _proactive_engine = ProactiveEngine()
    _proactive_engine.start()
    print("[PROACTIVE] ✓ Proactive engagement initialized")

def process_message(message: str):
    """Process message for proactive opportunities."""
    if _proactive_engine:
        _proactive_engine.process_user_message(message)

def get_engine():
    """Get proactive engine instance."""
    return _proactive_engine