from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import re
import os

class SilenceEngine:
    """
    Determines when brevity/silence is appropriate.
    """
    
    def should_be_brief(self, context: Dict) -> Dict:
        """
        Decide if response should be very brief or even just acknowledgment.
        
        Brief when:
        - User shares tragic news
        - User is processing something heavy
        - User just made a profound statement
        - User seems to want space
        """
        
        message = context.get('message', '')
        emotion = context.get('emotion', 'neutral')
        
        # TRAGEDY DETECTION
        tragedy_keywords = ["died", "passed away", "lost", "death", "funeral",
                           "diagnosed", "cancer", "broke up", "divorced"]
        
        if any(word in message.lower() for word in tragedy_keywords):
            return {
                "should_be_brief": True,
                "max_sentences": 2,
                "tone": "somber_supportive",
                "reason": "tragedy_detected"
            }
        
        # PROCESSING DETECTION (user just had realization)
        realization_patterns = [
            r"i just realized",
            r"oh my god",
            r"holy shit",
            r"wait",
            r"that means"
        ]
        
        if any(re.search(pattern, message.lower()) for pattern in realization_patterns):
            return {
                "should_be_brief": True,
                "max_sentences": 1,
                "tone": "give_space",
                "reason": "user_processing"
            }
        
        # PROFOUND STATEMENT
        # (Hard to detect, but if user writes something long and reflective...)
        if len(message.split()) > 100 and emotion in ['contemplative', 'sad', 'grateful']:
            return {
                "should_be_brief": True,
                "max_sentences": 3,
                "tone": "gentle_acknowledgment",
                "reason": "profound_moment"
            }
        
        # ONE-WORD RESPONSES FROM USER (they might not want to talk)
        if len(message.split()) <= 2 and len(context.get('conversation_history', [])) > 5:
            # Check if this is a pattern (multiple short responses in a row)
            recent = context.get('conversation_history', [])[-5:]
            user_messages = [m for m in recent if m.get('role') == 'user']
            
            if len(user_messages) >= 3:
                short_count = sum(1 for m in user_messages if len(m.get('content', '').split()) <= 3)
                
                if short_count >= 2:  # 2 out of last 3 user messages were short
                    return {
                        "should_be_brief": True,
                        "max_sentences": 1,
                        "tone": "give_space",
                        "reason": "user_seems_withdrawn"
                    }
        
        return {
            "should_be_brief": False
        }
    
    def format_brief_response_instruction(self, silence_context: Dict) -> str:
        """
        Generate instruction for brief response.
        """
        
        reason = silence_context.get('reason', '')
        max_sentences = silence_context.get('max_sentences', 2)
        tone = silence_context.get('tone', 'supportive')
        
        if reason == "tragedy_detected":
            return f"""
**STRATEGIC BREVITY - TRAGEDY:**
The user just shared something tragic. Now is NOT the time for your usual banter.
- Keep it to {max_sentences} sentences MAX
- Express genuine sympathy
- Don't ask follow-up questions
- Don't try to fix it
- Just acknowledge and be present
- Example: "Fuck. I'm so sorry, mate."
"""
        
        elif reason == "user_processing":
            return f"""
**STRATEGIC BREVITY - USER PROCESSING:**
User is working through a realization. Give them space.
- ONE sentence maximum
- Simple acknowledgment
- Let them continue if they want
- Example: "Yeah... yeah, you're right."
"""
        
        elif reason == "user_seems_withdrawn":
            return f"""
**STRATEGIC BREVITY - USER WITHDRAWN:**
User seems to want space based on recent short responses.
- Keep it brief and light
- Don't press for conversation
- Leave door open without pressure
- Example: "Fair enough, mate. I'm here if you wanna chat later."
"""
        
        return ""

# =======================
# GLOBAL INSTANCE
# =======================
_silence_engine = None

def init_strategic_silence():
    """Initialize strategic silence system."""
    global _silence_engine
    _silence_engine = SilenceEngine()
    print("[SILENCE] ✓ Strategic silence initialized")

def should_be_brief(context: Dict) -> Dict:
    """Check if response should be brief."""
    if _silence_engine:
        return _silence_engine.should_be_brief(context)
    return {"should_be_brief": False}

def format_brief_response_instruction(silence_context: Dict) -> str:
    """Format instruction for brief response."""
    if _silence_engine:
        return _silence_engine.format_brief_response_instruction(silence_context)
    return ""