# memory_management/emotion.py
import random

# =======================
# EMOTION ASSIGNMENT
# =======================
# Basic list of emotions for tagging
EMOTIONS = [
    "happy",
    "sad",
    "angry",
    "neutral",
    "confused",
    "excited",
    "frustrated",
    "curious",
    "playful",
    "anxious"
]

# Simple keyword-based overrides
EMOTION_KEYWORDS = {
    "love": "happy",
    "hate": "angry",
    "sad": "sad",
    "happy": "happy",
    "angry": "angry",
    "confused": "confused",
    "frustrated": "frustrated",
    "excited": "excited",
    "lol": "playful",
    "haha": "playful",
    "worried": "anxious",
}

def assign_emotion(text: str) -> str:
    """
    Assigns a simple emotion tag based on keywords.
    Defaults to a weighted random choice if none found.
    """
    if not isinstance(text, str) or not text.strip():
        return "neutral"

    text_lower = text.lower()
    for keyword, emotion in EMOTION_KEYWORDS.items():
        if keyword in text_lower:
            return emotion

    # fallback random choice biased toward neutral
    weighted_emotions = EMOTIONS + ["neutral"] * 3
    return random.choice(weighted_emotions)
