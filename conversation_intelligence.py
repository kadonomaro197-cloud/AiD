# Persona/conversation_intelligence.py
"""
Conversation Intelligence
Decides HOW to engage in conversation.
"""

from typing import Dict, Optional

class ConversationIntelligence:
    """Analyzes conversation flow and decides engagement strategy."""
    
    def __init__(self):
        pass
    
    def analyze_message(self, user_message: str, context: Dict) -> Dict:
        """
        Analyze message and return conversation strategy.
        
        Returns:
            {
                "should_ask_followup": bool,
                "followup_question": Optional[str],
                "depth_preference": "brief" | "moderate" | "deep",
                "tone_adjustment": str,
                "special_instructions": str
            }
        """
        strategy = {
            "should_ask_followup": False,
            "followup_question": None,
            "depth_preference": "moderate",
            "tone_adjustment": "",
            "special_instructions": ""
        }
        
        msg_lower = user_message.lower()
        msg_length = len(user_message.split())
        
        # === FOLLOW-UP DETECTION ===
        # User mentioned something vague
        if any(word in msg_lower for word in ["it", "that", "thing", "stuff"]) and msg_length < 20:
            strategy["should_ask_followup"] = True
            strategy["followup_question"] = "What specifically are you referring to?"
        
        # User mentioned problem without details
        elif any(word in msg_lower for word in ["problem", "issue", "broken", "not working"]) and msg_length < 15:
            strategy["should_ask_followup"] = True
            strategy["followup_question"] = "What's going on with it? Give me the details."
        
        # User seems excited but brief
        elif "!" in user_message and msg_length < 10:
            strategy["should_ask_followup"] = True
            strategy["followup_question"] = "Tell me more! What happened?"
        
        # User trailing off (...)
        elif user_message.endswith("...") or user_message.endswith(".."):
            strategy["should_ask_followup"] = True
            strategy["followup_question"] = "Go on, mate. What's on your mind?"
        
        # === DEPTH PREFERENCE ===
        if msg_length > 50:
            # User wrote a lot - they want depth
            strategy["depth_preference"] = "deep"
            strategy["special_instructions"] = "User wrote a detailed message. Match their depth. Be thoughtful and thorough."
        
        elif msg_length < 10:
            # User wrote very little - keep it brief
            strategy["depth_preference"] = "brief"
            strategy["special_instructions"] = "User sent a short message. Keep response concise (2-3 sentences max)."
        
        # === READING BETWEEN THE LINES ===
        # User says they're fine but...
        if "fine" in msg_lower or "okay" in msg_lower or "ok" in msg_lower:
            if any(word in msg_lower for word in ["i guess", "whatever", "doesn't matter"]):
                strategy["tone_adjustment"] = "supportive"
                strategy["special_instructions"] += " User says they're fine but language suggests otherwise. Be gently supportive without being pushy."
        
        # User asks "why" - they want reasoning
        if msg_lower.startswith("why"):
            strategy["depth_preference"] = "deep"
            strategy["special_instructions"] += " User asked 'why' - provide reasoning and explanation, not just facts."
        
        # User says "just tell me" or "simple answer"
        if "just tell me" in msg_lower or "simple" in msg_lower or "quick" in msg_lower:
            strategy["depth_preference"] = "brief"
            strategy["special_instructions"] += " User wants brevity. Direct answer, no fluff."
        
        # === CHALLENGE VS AGREE ===
        # If user makes absolute statement ("always", "never", "everyone")
        if any(word in msg_lower for word in ["always", "never", "everyone", "nobody", "all"]):
            # Don't challenge on emotional topics
            emotional_words = ["hate", "love", "scared", "afraid", "excited"]
            is_emotional = any(word in msg_lower for word in emotional_words)
            
            if not is_emotional:
                strategy["tone_adjustment"] = "challenging"
                strategy["special_instructions"] += " User made absolute statement. Gently offer alternative perspective if appropriate."
        
        return strategy
    
    def format_system_prompt_addition(self, strategy: Dict) -> str:
        """Convert strategy into system prompt instructions."""
        
        additions = []
        
        if strategy["special_instructions"]:
            additions.append(f"**CONVERSATION STRATEGY:**\n{strategy['special_instructions']}")
        
        if strategy["should_ask_followup"] and strategy["followup_question"]:
            additions.append(f"\n**FOLLOW-UP SUGGESTION:**\nConsider asking: \"{strategy['followup_question']}\"")
        
        if strategy["depth_preference"] == "brief":
            additions.append("\n**BREVITY MODE:** Keep response under 3 sentences.")
        elif strategy["depth_preference"] == "deep":
            additions.append("\n**DEPTH MODE:** User wants thorough engagement. Provide detailed, thoughtful response.")
        
        if strategy["tone_adjustment"] == "supportive":
            additions.append("\n**TONE:** Be supportive and empathetic.")
        elif strategy["tone_adjustment"] == "challenging":
            additions.append("\n**TONE:** You can respectfully offer an alternative perspective here.")
        
        return "\n".join(additions)

# =======================
# GLOBAL INSTANCE
# =======================
_conversation_intelligence = None

def init_conversation_intelligence():
    """Initialize conversation intelligence."""
    global _conversation_intelligence
    _conversation_intelligence = ConversationIntelligence()
    print("[CONVERSATION] ✓ Conversation intelligence initialized")

def analyze_message(user_message: str, context: Dict = None) -> Dict:
    """Analyze message for conversation strategy."""
    if _conversation_intelligence is None:
        init_conversation_intelligence()
    
    return _conversation_intelligence.analyze_message(user_message, context or {})

def get_prompt_addition(strategy: Dict) -> str:
    """Get system prompt addition from strategy."""
    if _conversation_intelligence:
        return _conversation_intelligence.format_system_prompt_addition(strategy)
    return ""