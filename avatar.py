"""
Avatar System - Phase 4
Visual expressions and avatar management
"""

from typing import Optional
from enum import Enum


class AvatarExpression(Enum):
    """Predefined avatar expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    SAD = "sad"
    THINKING = "thinking"
    SURPRISED = "surprised"
    CONCERNED = "concerned"
    PLAYFUL = "playful"
    CONFIDENT = "confident"


class AvatarSystem:
    """
    Manages AiD's avatar expressions and visual representation.
    """
    
    def __init__(self):
        self.current_expression = AvatarExpression.NEUTRAL
        self.expression_history = []
    
    def set_expression(self, expression: AvatarExpression):
        """Set current avatar expression."""
        self.current_expression = expression
        self.expression_history.append({
            'expression': expression.value,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
        print(f"[AVATAR] Expression set to: {expression.value}")
    
    def get_expression(self) -> AvatarExpression:
        """Get current expression."""
        return self.current_expression
    
    def set_from_emotion(self, emotion: str):
        """Set expression based on detected emotion."""
        emotion_to_expression = {
            'happy': AvatarExpression.HAPPY,
            'excited': AvatarExpression.EXCITED,
            'sad': AvatarExpression.SAD,
            'anxious': AvatarExpression.CONCERNED,
            'angry': AvatarExpression.NEUTRAL,  # Keep neutral for negative
            'proud': AvatarExpression.CONFIDENT,
            'grateful': AvatarExpression.HAPPY,
            'calm': AvatarExpression.NEUTRAL,
            'tired': AvatarExpression.NEUTRAL,
        }
        
        expression = emotion_to_expression.get(emotion, AvatarExpression.NEUTRAL)
        self.set_expression(expression)
    
    def get_expression_emoji(self) -> str:
        """Get emoji representation of current expression."""
        emoji_map = {
            AvatarExpression.NEUTRAL: "😐",
            AvatarExpression.HAPPY: "😊",
            AvatarExpression.EXCITED: "🤩",
            AvatarExpression.SAD: "😔",
            AvatarExpression.THINKING: "🤔",
            AvatarExpression.SURPRISED: "😲",
            AvatarExpression.CONCERNED: "😟",
            AvatarExpression.PLAYFUL: "😏",
            AvatarExpression.CONFIDENT: "😎"
        }
        
        return emoji_map.get(self.current_expression, "😐")


# =======================
# GLOBAL INSTANCE
# =======================
_avatar = None

def get_avatar() -> AvatarSystem:
    """Get or create avatar instance."""
    global _avatar
    if _avatar is None:
        _avatar = AvatarSystem()
    return _avatar

def init_avatar():
    """Initialize avatar system."""
    get_avatar()
    print("[AVATAR] Avatar system initialized")

def set_expression(expression: AvatarExpression):
    """Set avatar expression."""
    get_avatar().set_expression(expression)

def set_from_emotion(emotion: str):
    """Set expression from emotion."""
    get_avatar().set_from_emotion(emotion)

def get_current_emoji() -> str:
    """Get current expression emoji."""
    return get_avatar().get_expression_emoji()
