# Persona/emotion_intelligence.py
"""
Emotional Intelligence System
Deep emotion understanding and adaptive responses.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# =======================
# EMOTION DETECTOR
# =======================
class EmotionDetector:
    """Enhanced emotion detection."""
    
    def __init__(self):
        self.emotion_patterns = {
            # Core emotions
            "joy": {
                "keywords": ["happy", "excited", "great", "awesome", "love", "amazing", 
                            "brilliant", "fantastic", "wonderful", "perfect"],
                "intensity_modifiers": ["so", "really", "very", "super", "extremely"],
                "punctuation": ["!", "!!!", ":)", "ðŸ˜Š", "ðŸ˜„", "ðŸŽ‰"]
            },
            "sadness": {
                "keywords": ["sad", "depressed", "down", "upset", "disappointed", 
                            "awful", "terrible", "horrible", "devastated"],
                "intensity_modifiers": ["really", "very", "so", "completely"],
                "punctuation": [":(", "ðŸ˜¢", "ðŸ˜”", "ðŸ˜ž"]
            },
            "anger": {
                "keywords": ["angry", "pissed", "furious", "mad", "frustrated", 
                            "annoyed", "irritated", "hate"],
                "intensity_modifiers": ["so", "really", "fucking", "damn"],
                "punctuation": ["!", "!!"]
            },
            "anxiety": {
                "keywords": ["worried", "anxious", "nervous", "scared", "afraid", 
                            "concerned", "stressed", "overwhelmed"],
                "intensity_modifiers": ["really", "very", "so", "super"],
                "punctuation": ["..."]
            },
            "excitement": {
                "keywords": ["excited", "pumped", "hyped", "can't wait", "omg", 
                            "finally", "yes"],
                "intensity_modifiers": ["so", "really", "super"],
                "punctuation": ["!", "!!!", "ðŸŽ‰", "ðŸ”¥"]
            },
            "frustration": {
                "keywords": ["frustrated", "stuck", "can't figure", "ugh", "dammit", 
                            "why", "struggling"],
                "intensity_modifiers": ["so", "really", "fucking"],
                "punctuation": ["...", "!"]
            },
            "pride": {
                "keywords": ["proud", "accomplished", "achieved", "finished", "nailed", 
                            "crushed", "killed it", "PR", "finally"],
                "intensity_modifiers": ["so", "really", "super"],
                "punctuation": ["!", "ðŸ’ª", "ðŸŽ‰"]
            },
            "confusion": {
                "keywords": ["confused", "don't understand", "what", "huh", "unclear", 
                            "lost", "not sure"],
                "intensity_modifiers": ["really", "so", "completely"],
                "punctuation": ["?", "??", "???"]
            }
        }
    
    def detect(self, message: str) -> Dict:
        """
        Detect emotion with confidence and intensity.
        Returns: {emotion, confidence, intensity, context}
        """
        msg_lower = message.lower()
        detected = []
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            
            # Check keywords
            keyword_matches = sum(1 for kw in patterns["keywords"] if kw in msg_lower)
            score += keyword_matches * 2
            
            # Check intensity modifiers
            modifier_matches = sum(1 for mod in patterns["intensity_modifiers"] if mod in msg_lower)
            intensity_boost = modifier_matches * 0.5
            
            # Check punctuation
            punct_matches = sum(1 for p in patterns["punctuation"] if p in message)
            score += punct_matches * 0.5
            
            if score > 0:
                confidence = min(score / 5.0, 1.0)  # Normalize to 0-1
                intensity = min((score + intensity_boost) / 6.0, 1.0)
                
                detected.append({
                    "emotion": emotion,
                    "confidence": confidence,
                    "intensity": intensity,
                    "signals": {
                        "keywords": keyword_matches,
                        "modifiers": modifier_matches,
                        "punctuation": punct_matches
                    }
                })
        
        # Sort by confidence
        detected.sort(key=lambda x: x["confidence"], reverse=True)
        
        if detected:
            primary = detected[0]
            secondary = detected[1:3]  # Top 2 secondary emotions
            
            return {
                "primary": primary,
                "secondary": secondary,
                "timestamp": datetime.now().isoformat(),
                "message_context": message[:100]
            }
        
        # Default neutral
        return {
            "primary": {"emotion": "neutral", "confidence": 0.5, "intensity": 0.3},
            "secondary": [],
            "timestamp": datetime.now().isoformat(),
            "message_context": message[:100]
        }

# =======================
# RESPONSE ADAPTER
# =======================
class ResponseAdapter:
    """Adapts response style based on emotion."""
    
    def __init__(self):
        self.response_modes = {
            "supportive": {
                "tone": "warm, empathetic, gentle",
                "approach": "listen, validate, comfort",
                "cockney_level": "moderate",  # Less sass, more warmth
                "example": "Aww mate, that's rough. I hear ya. Wanna talk about it?"
            },
            "celebratory": {
                "tone": "excited, enthusiastic, proud",
                "approach": "celebrate, amplify joy, match energy",
                "cockney_level": "high",  # Full personality
                "example": "Oi! That's bloody brilliant! Proper chuffed for ya, boss!"
            },
            "solution-focused": {
                "tone": "practical, clear, helpful",
                "approach": "problem-solve, offer options, be pragmatic",
                "cockney_level": "moderate",
                "example": "Right, let's sort this. What've you tried so far?"
            },
            "calming": {
                "tone": "steady, reassuring, grounding",
                "approach": "reduce anxiety, perspective, breathing room",
                "cockney_level": "low",  # More standard, less overwhelming
                "example": "Take a breath, mate. Let's break this down step by step."
            },
            "energizing": {
                "tone": "pumped, motivating, confident",
                "approach": "hype up, encourage, push forward",
                "cockney_level": "high",
                "example": "C'mon boss! You got this! Let's smash it!"
            },
            "challenging": {
                "tone": "direct, honest, respectful",
                "approach": "push thinking, offer alternative view, constructive",
                "cockney_level": "moderate",
                "example": "Mate, I'mma be real with ya - have you considered...?"
            }
        }
    
    def determine_mode(self, emotion_data: Dict) -> str:
        """Determine appropriate response mode."""
        # ... existing logic
        primary_emotion = emotion_data["primary"]["emotion"]
        intensity = emotion_data["primary"]["intensity"]
        
        # Map emotions to response modes
        emotion_to_mode = {
            "joy": "celebratory",
            "excitement": "celebratory",
            "pride": "celebratory",
            "sadness": "supportive",
            "anxiety": "calming",
            "anger": "calming" if intensity > 0.7 else "supportive",
            "frustration": "solution-focused",
            "confusion": "solution-focused",
            "neutral": "energizing"  # Default to upbeat
        }
        
        mode = emotion_to_mode.get(primary_emotion, "supportive")
        
        return mode
    
    def get_system_prompt_addition(self, mode: str, emotion_data: Dict) -> str:
        """Get additional system prompt based on mode."""
        mode_data = self.response_modes[mode]
        
        prompt = f"""
**EMOTIONAL CONTEXT:**
User is currently feeling: {emotion_data['primary']['emotion']} (intensity: {emotion_data['primary']['intensity']:.1f}/1.0)

**RESPONSE MODE: {mode.upper()}**
- Tone: {mode_data['tone']}
- Approach: {mode_data['approach']}
- Personality level: {mode_data['cockney_level']}

Example response style: "{mode_data['example']}"

Adapt your response to match this emotional context while maintaining your core Cockney personality.
"""
        return prompt

# =======================
# EMOTIONAL MEMORY
# =======================
class EmotionalMemory:
    """Tracks emotional patterns over time."""
    
    def __init__(self):
        self.emotion_history = []
        self.load_history()
    
    def record_emotion(self, emotion_data: Dict):
        """Record emotion event."""
        self.emotion_history.append(emotion_data)
        
        # Keep last 100 emotions
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
        
        self.save_history()
    
    def get_recent_pattern(self, days: int = 7) -> Dict:
        """Analyze emotional patterns over recent days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = [e for e in self.emotion_history 
                 if datetime.fromisoformat(e["timestamp"]) > cutoff]
        
        if not recent:
            return {"trend": "neutral", "note": "Not enough data"}
        
        # Count primary emotions
        emotion_counts = {}
        for entry in recent:
            emotion = entry["primary"]["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Determine trend
        total = len(recent)
        positive = emotion_counts.get("joy", 0) + emotion_counts.get("excitement", 0) + emotion_counts.get("pride", 0)
        negative = emotion_counts.get("sadness", 0) + emotion_counts.get("anxiety", 0) + emotion_counts.get("anger", 0) + emotion_counts.get("frustration", 0)
        
        positive_ratio = positive / total
        negative_ratio = negative / total
        
        if positive_ratio > 0.6:
            trend = "positive"
            note = "You've been in good spirits lately"
        elif negative_ratio > 0.6:
            trend = "struggling"
            note = "You seem to be having a rough time lately"
        elif negative_ratio > 0.4:
            trend = "mixed"
            note = "Bit of a rollercoaster lately, innit?"
        else:
            trend = "neutral"
            note = "Pretty steady"
        
        return {
            "trend": trend,
            "note": note,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "dominant_emotion": max(emotion_counts, key=emotion_counts.get),
            "period_days": days,
            "sample_size": total
        }
    
    def save_history(self):
        """Save emotion history."""
        try:
            with open("Persona/data/emotion_history.json", "w") as f:
                json.dump(self.emotion_history, f, indent=2)
        except Exception as e:
            print(f"[EMOTION] Error saving history: {e}")
    
    def load_history(self):
        """Load emotion history."""
        try:
            with open("Persona/data/emotion_history.json", "r") as f:
                self.emotion_history = json.load(f)
        except:
            self.emotion_history = []

# =======================
# MAIN INTELLIGENCE ENGINE
# =======================
class EmotionalIntelligence:
    """Main emotional intelligence coordinator."""
    
    def __init__(self):
        self.detector = EmotionDetector()
        self.adapter = ResponseAdapter()
        self.memory = EmotionalMemory()
    
    def process_message(self, message: str) -> Dict:
        """
        Process message for emotional intelligence.
        Returns complete emotional context for response generation.
        """
        # Detect emotion
        emotion_data = self.detector.detect(message)
        
        # Record in memory
        self.memory.record_emotion(emotion_data)
        
        # Determine response mode
        response_mode = self.adapter.determine_mode(emotion_data)
        
        # Get recent emotional pattern
        pattern = self.memory.get_recent_pattern(days=7)
        
        # Build complete context
        context = {
            "current_emotion": emotion_data,
            "response_mode": response_mode,
            "system_prompt_addition": self.adapter.get_system_prompt_addition(response_mode, emotion_data),
            "recent_pattern": pattern,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[EMOTION] Detected: {emotion_data['primary']['emotion']} "
              f"(confidence: {emotion_data['primary']['confidence']:.2f}, "
              f"intensity: {emotion_data['primary']['intensity']:.2f})")
        print(f"[EMOTION] Response mode: {response_mode}")
        print(f"[EMOTION] Recent trend: {pattern['trend']} - {pattern['note']}")
        
        return context

# =======================
# GLOBAL INSTANCE
# =======================
_emotional_intelligence = None

def init_emotional_intelligence():
    """Initialize emotional intelligence system."""
    global _emotional_intelligence
    _emotional_intelligence = EmotionalIntelligence()
    print("[EMOTION] âœ“ Emotional intelligence initialized")

def process_message(message: str) -> Dict:
    """Process message for emotional context."""
    if _emotional_intelligence is None:
        init_emotional_intelligence()
    
    return _emotional_intelligence.process_message(message)

def get_recent_pattern(days: int = 7) -> Dict:
    """Get recent emotional pattern."""
    if _emotional_intelligence:
        return _emotional_intelligence.memory.get_recent_pattern(days)
    return {}