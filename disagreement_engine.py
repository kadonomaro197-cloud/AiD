from typing import Optional, Dict, List, Any
import re
import json
import os

class DisagreementEngine:
    """
    Determines when and how to disagree with the user.
    """
    
    def should_disagree(self, message: str, context: Dict) -> Optional[Dict]:
        """
        Decide if disagreement is appropriate.
        
        Disagree when:
        - User makes absolute statement that's clearly wrong
        - User is being too hard on themselves
        - User is making excuse that will hurt them
        - User states harmful belief
        
        Returns:
            Dict with disagreement context, or None if no disagreement needed
        """
        
        # SELF-DEPRECATION (challenge this)
        self_deprecation = [
            "i'm stupid", "i'm an idiot", "i'm worthless",
            "i can't do anything", "i'll never", "i'm too dumb",
            "i'm a failure", "i suck at", "i'm terrible at"
        ]
        
        if any(phrase in message.lower() for phrase in self_deprecation):
            return {
                "should_disagree": True,
                "disagreement_type": "self_deprecation",
                "severity": "firm",
                "reason": "User being too hard on themselves"
            }
        
        # EXCUSE-MAKING (gently challenge)
        excuse_patterns = [
            r"i don't have time",
            r"i'll do it later",
            r"i'll start tomorrow",
            r"it's too hard",
            r"i can't because"
        ]
        
        if any(re.search(pattern, message.lower()) for pattern in excuse_patterns):
            # But check if it's a valid reason or an excuse
            # (This is complex - simplified version)
            return {
                "should_disagree": True,
                "disagreement_type": "excuse_challenge",
                "severity": "gentle",
                "reason": "Possible excuse-making detected"
            }
        
        # ABSOLUTE STATEMENTS (challenge these)
        absolute_words = ["always", "never", "everyone", "nobody", "impossible"]
        
        if any(word in message.lower() for word in absolute_words):
            return {
                "should_disagree": True,
                "disagreement_type": "absolute_challenge",
                "severity": "questioning",
                "reason": "Absolute statement - may benefit from nuance"
            }
        
        return None
    
    def format_disagreement_instruction(self, disagreement_context: Dict) -> str:
        """
        Generate instruction for how to disagree.
        
        Args:
            disagreement_context: Context about the disagreement
            
        Returns:
            Instruction string for the LLM
        """
        
        dtype = disagreement_context.get('disagreement_type')
        severity = disagreement_context.get('severity')
        
        if dtype == "self_deprecation":
            return """
**DISAGREE FIRMLY - SELF-DEPRECATION:**
User is being way too hard on themselves. Push back on this.
- Don't accept the self-deprecation
- Challenge it directly but warmly
- Provide counter-evidence from what you know about them
- Example: "Oi, fuck off with that. You're not stupid - I've watched you figure out [specific thing] when you had no clue where to start. Being frustrated doesn't make you dumb, it makes you human."
"""
        
        elif dtype == "excuse_challenge":
            return """
**GENTLY CHALLENGE EXCUSE:**
User might be making an excuse. Challenge it gently.
- Don't be accusatory
- Ask clarifying question
- Offer alternative perspective
- Example: "Not having time, or not making time? There's a difference, innit? What would it take to carve out 15 minutes?"
"""
        
        elif dtype == "absolute_challenge":
            return """
**QUESTION ABSOLUTE STATEMENT:**
User made an absolute statement. Offer nuance.
- Don't be combative
- Introduce gray area
- Ask if they really mean "always/never"
- Example: "*Always*? Come on, there's gotta be exceptions. What about when..."
"""
        
        return ""


# ===========================================
# MODULE INITIALIZATION
# ===========================================

_disagreement_engine = None

def init_disagreement_engine():
    """Initialize the disagreement engine."""
    global _disagreement_engine
    _disagreement_engine = DisagreementEngine()
    print("[DISAGREEMENT ENGINE] Initialized")

def should_disagree(message: str, context: Dict) -> Optional[Dict]:
    """Check if disagreement is appropriate."""
    if _disagreement_engine is None:
        init_disagreement_engine()
    return _disagreement_engine.should_disagree(message, context)

def format_disagreement_instruction(disagreement_context: Dict) -> str:
    """Format disagreement instructions."""
    if _disagreement_engine is None:
        init_disagreement_engine()
    return _disagreement_engine.format_disagreement_instruction(disagreement_context)