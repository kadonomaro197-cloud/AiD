"""
Emotion-Driven Voice Parameter Mapping
Maps detected emotions to voice configuration parameters for dynamic, context-aware speech.
"""

from typing import Dict, Optional
from voice_config import VoiceConfig
import random


class EmotionVoiceMapper:
    """
    Maps emotions and contexts to voice parameters.
    Allows AiD's voice to adapt based on her emotional state.
    """

    # =======================
    # EMOTION → VOICE PARAMETER MAPPINGS
    # =======================

    EMOTION_PRESETS = {
        # Positive emotions
        "joy": {
            "temperature": 0.75,
            "repetition_penalty": 2.0,
            "length_penalty": 0.9,
            "top_k": 70,
            "top_p": 0.88,
            "speed": 1.1,
            "enable_text_splitting": True,
            "description": "Happy, upbeat, slightly faster"
        },
        "happy": {
            "temperature": 0.72,
            "repetition_penalty": 2.2,
            "length_penalty": 0.95,
            "top_k": 65,
            "top_p": 0.87,
            "speed": 1.05,
            "enable_text_splitting": True,
            "description": "Content, warm"
        },
        "excitement": {
            "temperature": 0.80,
            "repetition_penalty": 1.8,
            "length_penalty": 0.85,
            "top_k": 75,
            "top_p": 0.90,
            "speed": 1.15,
            "enable_text_splitting": False,
            "description": "Excited, energetic, fast-paced"
        },
        "excited": {
            "temperature": 0.80,
            "repetition_penalty": 1.8,
            "length_penalty": 0.85,
            "top_k": 75,
            "top_p": 0.90,
            "speed": 1.15,
            "enable_text_splitting": False,
            "description": "Excited, energetic"
        },
        "pride": {
            "temperature": 0.68,
            "repetition_penalty": 2.5,
            "length_penalty": 1.0,
            "top_k": 55,
            "top_p": 0.85,
            "speed": 1.0,
            "enable_text_splitting": True,
            "description": "Proud, confident, measured"
        },
        "playful": {
            "temperature": 0.78,
            "repetition_penalty": 2.0,
            "length_penalty": 0.88,
            "top_k": 70,
            "top_p": 0.89,
            "speed": 1.08,
            "enable_text_splitting": True,
            "description": "Playful, teasing, varied"
        },

        # Negative emotions
        "sadness": {
            "temperature": 0.55,
            "repetition_penalty": 3.0,
            "length_penalty": 1.2,
            "top_k": 40,
            "top_p": 0.80,
            "speed": 0.92,
            "enable_text_splitting": True,
            "description": "Sad, slower, softer"
        },
        "sad": {
            "temperature": 0.55,
            "repetition_penalty": 3.0,
            "length_penalty": 1.2,
            "top_k": 40,
            "top_p": 0.80,
            "speed": 0.92,
            "enable_text_splitting": True,
            "description": "Sad, contemplative"
        },
        "anger": {
            "temperature": 0.62,
            "repetition_penalty": 3.5,
            "length_penalty": 0.88,
            "top_k": 45,
            "top_p": 0.82,
            "speed": 1.05,
            "enable_text_splitting": False,
            "description": "Angry, sharp, direct"
        },
        "angry": {
            "temperature": 0.62,
            "repetition_penalty": 3.5,
            "length_penalty": 0.88,
            "top_k": 45,
            "top_p": 0.82,
            "speed": 1.05,
            "enable_text_splitting": False,
            "description": "Angry, intense"
        },
        "frustration": {
            "temperature": 0.65,
            "repetition_penalty": 3.2,
            "length_penalty": 0.95,
            "top_k": 50,
            "top_p": 0.83,
            "speed": 1.02,
            "enable_text_splitting": True,
            "description": "Frustrated, slightly tense"
        },
        "frustrated": {
            "temperature": 0.65,
            "repetition_penalty": 3.2,
            "length_penalty": 0.95,
            "top_k": 50,
            "top_p": 0.83,
            "speed": 1.02,
            "enable_text_splitting": True,
            "description": "Frustrated"
        },
        "anxiety": {
            "temperature": 0.60,
            "repetition_penalty": 2.8,
            "length_penalty": 1.05,
            "top_k": 42,
            "top_p": 0.81,
            "speed": 1.08,
            "enable_text_splitting": True,
            "description": "Anxious, slightly faster, tense"
        },
        "anxious": {
            "temperature": 0.60,
            "repetition_penalty": 2.8,
            "length_penalty": 1.05,
            "top_k": 42,
            "top_p": 0.81,
            "speed": 1.08,
            "enable_text_splitting": True,
            "description": "Anxious, worried"
        },

        # Neutral/Other emotions
        "neutral": {
            "temperature": 0.65,
            "repetition_penalty": 2.5,
            "length_penalty": 1.0,
            "top_k": 50,
            "top_p": 0.85,
            "speed": 1.0,
            "enable_text_splitting": True,
            "description": "Neutral, balanced"
        },
        "confusion": {
            "temperature": 0.63,
            "repetition_penalty": 2.6,
            "length_penalty": 1.08,
            "top_k": 48,
            "top_p": 0.84,
            "speed": 0.98,
            "enable_text_splitting": True,
            "description": "Confused, questioning, slower"
        },
        "confused": {
            "temperature": 0.63,
            "repetition_penalty": 2.6,
            "length_penalty": 1.08,
            "top_k": 48,
            "top_p": 0.84,
            "speed": 0.98,
            "enable_text_splitting": True,
            "description": "Confused"
        },
        "curious": {
            "temperature": 0.70,
            "repetition_penalty": 2.3,
            "length_penalty": 1.0,
            "top_k": 60,
            "top_p": 0.86,
            "speed": 1.02,
            "enable_text_splitting": True,
            "description": "Curious, inquisitive"
        },
    }

    # =======================
    # REFERENCE SAMPLE MAPPING
    # =======================
    # Map emotions to specific voice sample indices (0-16 for your 17 samples)
    # Adjust these after listening to your samples and identifying their emotional tones

    EMOTION_SAMPLE_MAP = {
        # Example mapping - customize based on your actual samples
        "joy": [0, 1],           # Use samples 0-1 for happy emotions
        "happy": [0, 1],
        "excitement": [2, 3],    # Use samples 2-3 for excited emotions
        "excited": [2, 3],
        "neutral": [4, 5, 6],    # Use samples 4-6 for neutral
        "sad": [7, 8],           # Use samples 7-8 for sad emotions
        "sadness": [7, 8],
        "angry": [9, 10],        # Use samples 9-10 for angry emotions
        "anger": [9, 10],
        "frustrated": [11, 12],
        "frustration": [11, 12],
        "anxious": [13, 14],
        "anxiety": [13, 14],
        "curious": [15, 16],
        "confused": [15, 16],
        "confusion": [15, 16],
        "playful": [0, 1, 2],
        "pride": [4, 5],
    }

    @classmethod
    def apply_emotion(cls, emotion: str, intensity: float = 0.5) -> None:
        """
        Apply voice parameters based on detected emotion and intensity.

        Args:
            emotion: Detected emotion (e.g., "joy", "sadness", "neutral")
            intensity: Emotion intensity (0.0 to 1.0)
        """
        # Get emotion preset or default to neutral
        emotion_lower = emotion.lower()
        preset = cls.EMOTION_PRESETS.get(emotion_lower, cls.EMOTION_PRESETS["neutral"])

        # Apply base parameters
        VoiceConfig.TEMPERATURE = preset["temperature"]
        VoiceConfig.REPETITION_PENALTY = preset["repetition_penalty"]
        VoiceConfig.LENGTH_PENALTY = preset["length_penalty"]
        VoiceConfig.TOP_K = preset["top_k"]
        VoiceConfig.TOP_P = preset["top_p"]
        VoiceConfig.SPEED = preset["speed"]
        VoiceConfig.ENABLE_TEXT_SPLITTING = preset["enable_text_splitting"]

        # Adjust parameters based on intensity
        # Higher intensity = more extreme parameters
        if intensity > 0.7:
            # High intensity: exaggerate the emotion
            if emotion_lower in ["joy", "excitement", "excited", "playful"]:
                VoiceConfig.SPEED *= 1.05  # Even faster for high-intensity positive
                VoiceConfig.TEMPERATURE += 0.05
            elif emotion_lower in ["sadness", "sad", "anxiety", "anxious"]:
                VoiceConfig.SPEED *= 0.95  # Even slower for high-intensity negative
                VoiceConfig.LENGTH_PENALTY *= 1.1
            elif emotion_lower in ["anger", "angry", "frustration", "frustrated"]:
                VoiceConfig.REPETITION_PENALTY += 0.5  # More controlled for anger
                VoiceConfig.TEMPERATURE -= 0.05
        elif intensity < 0.3:
            # Low intensity: move closer to neutral
            neutral = cls.EMOTION_PRESETS["neutral"]
            VoiceConfig.TEMPERATURE = (VoiceConfig.TEMPERATURE + neutral["temperature"]) / 2
            VoiceConfig.SPEED = (VoiceConfig.SPEED + neutral["speed"]) / 2

        # Select appropriate reference sample
        sample_indices = cls.EMOTION_SAMPLE_MAP.get(emotion_lower, [0])
        VoiceConfig.REFERENCE_SAMPLE_INDEX = random.choice(sample_indices)

        print(f"[VOICE] Applied emotion: {emotion} (intensity: {intensity:.2f})")
        print(f"[VOICE] Using sample index: {VoiceConfig.REFERENCE_SAMPLE_INDEX}")
        print(f"[VOICE] Params: temp={VoiceConfig.TEMPERATURE:.2f}, speed={VoiceConfig.SPEED:.2f}")

    @classmethod
    def apply_context(cls, context: str) -> None:
        """
        Apply voice parameters based on conversational context.

        Args:
            context: Context type (e.g., "explanation", "greeting", "question", "command")
        """
        context_presets = {
            "explanation": {
                "temperature": 0.60,
                "speed": 0.95,
                "length_penalty": 1.05,
                "enable_text_splitting": True,
            },
            "greeting": {
                "temperature": 0.72,
                "speed": 1.05,
                "length_penalty": 0.95,
                "enable_text_splitting": False,
            },
            "question": {
                "temperature": 0.68,
                "speed": 1.0,
                "length_penalty": 1.0,
                "enable_text_splitting": True,
            },
            "command": {
                "temperature": 0.55,
                "speed": 1.08,
                "length_penalty": 0.90,
                "enable_text_splitting": False,
            },
            "storytelling": {
                "temperature": 0.75,
                "speed": 0.98,
                "length_penalty": 1.0,
                "enable_text_splitting": True,
            },
        }

        preset = context_presets.get(context.lower(), {})
        for param, value in preset.items():
            setattr(VoiceConfig, param.upper(), value)

        print(f"[VOICE] Applied context: {context}")

    @classmethod
    def apply_combined(cls, emotion: str, intensity: float, context: Optional[str] = None) -> None:
        """
        Apply both emotion and context parameters with intelligent blending.

        Args:
            emotion: Detected emotion
            intensity: Emotion intensity (0.0 to 1.0)
            context: Optional context type
        """
        # First apply emotion
        cls.apply_emotion(emotion, intensity)

        # Then adjust for context if provided
        if context:
            # Context makes smaller adjustments to emotion-based parameters
            if context == "explanation":
                VoiceConfig.SPEED *= 0.97  # Slightly slower for explanations
                VoiceConfig.ENABLE_TEXT_SPLITTING = True
            elif context == "greeting":
                VoiceConfig.SPEED *= 1.03  # Slightly faster for greetings
            elif context == "command":
                VoiceConfig.TEMPERATURE *= 0.95  # More controlled for commands
                VoiceConfig.ENABLE_TEXT_SPLITTING = False

    @classmethod
    def customize_sample_map(cls, emotion_sample_mapping: Dict[str, list]) -> None:
        """
        Customize the emotion-to-sample mapping after analyzing your voice samples.

        Args:
            emotion_sample_mapping: Dict mapping emotions to sample indices

        Example:
            mapper.customize_sample_map({
                "happy": [0, 1, 2],      # Samples 0-2 sound happy
                "sad": [3, 4],           # Samples 3-4 sound sad
                "neutral": [5, 6, 7],    # Samples 5-7 are neutral
            })
        """
        cls.EMOTION_SAMPLE_MAP.update(emotion_sample_mapping)
        print("[VOICE] Updated emotion-sample mapping:")
        for emotion, samples in emotion_sample_mapping.items():
            print(f"  {emotion}: samples {samples}")


# =======================
# CONVENIENCE FUNCTIONS
# =======================

def set_voice_for_emotion(emotion: str, intensity: float = 0.5, context: Optional[str] = None):
    """
    Convenience function to set voice parameters based on emotion.

    Usage:
        from emotion_voice_mapper import set_voice_for_emotion
        set_voice_for_emotion("happy", intensity=0.8)
        voice.speak("I'm so happy to see you!")
    """
    if context:
        EmotionVoiceMapper.apply_combined(emotion, intensity, context)
    else:
        EmotionVoiceMapper.apply_emotion(emotion, intensity)


def get_emotion_from_text(text: str) -> tuple:
    """
    Detect emotion from text and return (emotion, intensity).
    Integrates with existing emotion detection if available.

    Returns:
        tuple: (emotion_name, intensity_value)
    """
    try:
        # Try to use existing emotion intelligence system
        from emotion_intelligence import EmotionDetector
        detector = EmotionDetector()
        result = detector.detect(text)

        if result and len(result) > 0:
            top_emotion = result[0]
            return (top_emotion["emotion"], top_emotion["intensity"])
    except ImportError:
        pass

    # Fallback to simple emotion detection
    try:
        from emotion import assign_emotion
        emotion = assign_emotion(text)
        return (emotion, 0.5)  # Default medium intensity
    except ImportError:
        pass

    # Ultimate fallback
    return ("neutral", 0.5)
