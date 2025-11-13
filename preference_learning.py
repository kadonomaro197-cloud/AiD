# Persona/preference_learning.py
"""
Preference Learning Engine
Learns user preferences through observation.
"""

from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import json

class PreferenceEngine:
    """Learns and tracks user preferences."""
    
    def __init__(self):
        self.preferences = {
            "topics": defaultdict(lambda: {"mentions": 0, "positive_reactions": 0, "engagement_level": 0.0}),
            "response_styles": defaultdict(int),
            "conversation_depth": "moderate",  # shallow, moderate, deep
            "humor_reception": "positive",  # positive, neutral, negative
            "sass_tolerance": "high",  # low, moderate, high
            "initiative_preference": "balanced"  # passive, balanced, active
        }
        self.load_preferences()
    
    def learn_from_interaction(self, user_message: str, aid_response: str):
        """Learn from each interaction."""
        
        # Topic interest learning
        self._learn_topic_interest(user_message)
        
        # Response style learning
        self._learn_response_style_preference(user_message, aid_response)
        
        # Engagement depth learning
        self._learn_depth_preference(user_message)
        
        self.save_preferences()
    
    def _learn_topic_interest(self, message: str):
        """Learn which topics user engages with."""
        # Extract topics (simplified - use your NLP)
        words = message.lower().split()
        
        # Track multi-word topics
        potential_topics = []
        for i in range(len(words) - 1):
            two_word = f"{words[i]} {words[i+1]}"
            potential_topics.append(two_word)
        
        # Single meaningful words
        meaningful_words = [w for w in words if len(w) > 4 and w.isalpha()]
        potential_topics.extend(meaningful_words)
        
        for topic in potential_topics:
            self.preferences["topics"][topic]["mentions"] += 1
            
            # Message length indicates engagement
            engagement = min(len(message) / 200.0, 1.0)
            self.preferences["topics"][topic]["engagement_level"] = \
                (self.preferences["topics"][topic]["engagement_level"] * 0.8 + engagement * 0.2)
    
    def _learn_response_style_preference(self, user_message: str, aid_response: str):
        """Learn preferred response characteristics."""
        
        # If user responds quickly and positively after certain styles
        aid_style = self._analyze_response_style(aid_response)
        
        # Track which styles get positive reactions
        msg_lower = user_message.lower()
        positive_indicators = ["haha", "lol", "thanks", "perfect", "exactly", "yes", "love"]
        
        if any(ind in msg_lower for ind in positive_indicators):
            self.preferences["response_styles"][aid_style] += 1
    
    def _analyze_response_style(self, response: str) -> str:
        """Categorize AiD's response style."""
        if "!" in response and any(w in response.lower() for w in ["oi", "bloody", "proper"]):
            return "high_energy_cockney"
        elif "?" in response:
            return "inquisitive"
        elif len(response) > 200:
            return "detailed"
        elif any(w in response.lower() for w in ["mate", "boss", "innit"]):
            return "casual_friendly"
        else:
            return "neutral"
    
    def _learn_depth_preference(self, message: str):
        """Learn if user prefers shallow or deep conversations."""
        
        # Long, detailed messages → user likes depth
        # Short messages → user prefers brevity
        
        msg_length = len(message)
        
        if msg_length > 300:
            # User is providing depth
            if self.preferences["conversation_depth"] == "shallow":
                self.preferences["conversation_depth"] = "moderate"
            elif self.preferences["conversation_depth"] == "moderate":
                self.preferences["conversation_depth"] = "deep"
        
        elif msg_length < 50:
            # User prefers brevity
            if self.preferences["conversation_depth"] == "deep":
                self.preferences["conversation_depth"] = "moderate"
            elif self.preferences["conversation_depth"] == "moderate":
                self.preferences["conversation_depth"] = "shallow"
    
    def get_top_interests(self, n: int = 5) -> List[Dict]:
        """Get user's top interests by engagement."""
        topics = []
        for topic, data in self.preferences["topics"].items():
            if data["mentions"] >= 3:  # Minimum mentions
                score = data["mentions"] * data["engagement_level"]
                topics.append({
                    "topic": topic,
                    "score": score,
                    "mentions": data["mentions"],
                    "engagement": data["engagement_level"]
                })
        
        topics.sort(key=lambda x: x["score"], reverse=True)
        return topics[:n]
    
    def get_preference_context(self) -> str:
        """Get preference summary for system prompt."""
        top_interests = self.get_top_interests(3)
        
        context = f"""
**USER PREFERENCES:**
Conversation depth: {self.preferences['conversation_depth']}
Top interests: {', '.join([t['topic'] for t in top_interests])}
Preferred response style: {max(self.preferences['response_styles'], key=self.preferences['response_styles'].get) if self.preferences['response_styles'] else 'balanced'}
"""
        return context
    
    def save_preferences(self):
        """Save preferences to disk."""
        try:
            # Convert defaultdict to dict for JSON
            save_data = {
                "topics": dict(self.preferences["topics"]),
                "response_styles": dict(self.preferences["response_styles"]),
                "conversation_depth": self.preferences["conversation_depth"],
                "humor_reception": self.preferences["humor_reception"],
                "sass_tolerance": self.preferences["sass_tolerance"],
                "initiative_preference": self.preferences["initiative_preference"]
            }
            
            with open("Persona/data/preferences.json", "w") as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"[PREFERENCES] Error saving: {e}")
    
    def load_preferences(self):
        """Load preferences from disk."""
        try:
            with open("Persona/data/preferences.json", "r") as f:
                data = json.load(f)
                
                # Convert back to defaultdict
                self.preferences["topics"] = defaultdict(
                    lambda: {"mentions": 0, "positive_reactions": 0, "engagement_level": 0.0},
                    data.get("topics", {})
                )
                self.preferences["response_styles"] = defaultdict(int, data.get("response_styles", {}))
                self.preferences["conversation_depth"] = data.get("conversation_depth", "moderate")
                self.preferences["humor_reception"] = data.get("humor_reception", "positive")
                self.preferences["sass_tolerance"] = data.get("sass_tolerance", "high")
                self.preferences["initiative_preference"] = data.get("initiative_preference", "balanced")
        except:
            pass

# =======================
# GLOBAL INSTANCE
# =======================
_preference_engine = None

def init_preferences():
    """Initialize preference learning."""
    global _preference_engine
    _preference_engine = PreferenceEngine()
    print("[PREFERENCES] ✓ Preference learning initialized")

def learn_from_interaction(user_msg: str, aid_response: str):
    """Learn from interaction."""
    if _preference_engine:
        _preference_engine.learn_from_interaction(user_msg, aid_response)

def get_preference_context() -> str:
    """Get preference context for system prompt."""
    if _preference_engine:
        return _preference_engine.get_preference_context()
    return ""

def get_top_interests(n: int = 5):
    """Get top user interests."""
    if _preference_engine:
        return _preference_engine.get_top_interests(n)
    return []