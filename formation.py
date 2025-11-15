# memory_management/formation.py
"""
Memory formation system with reinforcement-based learning.
Prevents false memories by requiring multiple mentions before permanence.
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path
from .memory_vector_store import get_memory_store
from .scoring import extract_entities
import re

class MemoryFormation:
    """
    Manages memory creation with reinforcement-based learning.
    
    Reinforcement pattern:
    - First mention: Tracked but not permanent
    - Second mention (within 7 days): Still tracked
    - Third mention (within 30 days): Permanent memory created
    
    Immediate permanence for:
    - Explicit memory markers ("don't forget", "remember that")
    - Repeated emphasis (!!!, multiple mentions in single message)
    - User corrections/clarifications
    """
    
    def __init__(self, data_dir="memory_management/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.reinforcement_path = self.data_dir / "reinforcement_tracking.json"
        self.memory_store = get_memory_store()
        
        # Reinforcement tracking: {content_hash: {count, first_seen, last_seen, importance_signals}}
        self.reinforcement_buffer = {}
        self.load_reinforcement_buffer()
        
        print(f"[MEMORY FORMATION] Initialized with {len(self.reinforcement_buffer)} tracked concepts")
    
    def observe_interaction(self, user_message: str, aid_response: str = None) -> List[int]:
        """
        Observe an interaction and decide if memories should be formed.
        
        Args:
            user_message: User's message
            aid_response: AiD's response (optional, for context)
        
        Returns:
            List of memory IDs created (empty if none)
        """
        created_memory_ids = []
        
        # Extract potential memory candidates from user message
        candidates = self._extract_memory_candidates(user_message)
        
        for candidate in candidates:
            # Check for immediate permanence signals
            importance = self._detect_importance(user_message, candidate)

            if importance >= 1.8:
                # High importance - create memory immediately
                # (Includes: explicit markers, emotional content, identity statements)
                memory_id = self._create_memory(candidate, importance)
                created_memory_ids.append(memory_id)
                print(f"[MEMORY FORMATION] Immediate memory (importance={importance:.1f}): {candidate[:50]}...")
            else:
                # Normal importance - use reinforcement learning
                should_create = self._track_reinforcement(candidate)
                
                if should_create:
                    memory_id = self._create_memory(candidate, importance)
                    created_memory_ids.append(memory_id)
                    print(f"[MEMORY FORMATION] Reinforced memory: {candidate[:50]}...")
        
        # Save reinforcement buffer
        if candidates:
            self.save_reinforcement_buffer()

        # Save memory store to disk if new memories were created
        if created_memory_ids:
            self.memory_store.save_index()
            print(f"[MEMORY FORMATION] Saved {len(created_memory_ids)} new memories to disk")

        return created_memory_ids
    
    def _extract_memory_candidates(self, text: str) -> List[str]:
        """
        Extract potential memory candidates from text.
        Splits into semantic chunks (sentences or significant phrases).
        """
        candidates = []
        
        # Split by sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Filter criteria
            if len(sentence.split()) < 4:  # Too short
                continue
            if len(sentence) > 300:  # Too long, split further
                # Split long sentences by commas/semicolons
                sub_parts = re.split(r'[,;]+', sentence)
                candidates.extend([p.strip() for p in sub_parts if len(p.split()) >= 4])
            else:
                candidates.append(sentence)
        
        return candidates
    
    def _detect_importance(self, full_message: str, candidate: str) -> float:
        """
        Detect importance signals in the message.

        Returns importance multiplier:
        - 1.0: Normal statement
        - 1.5: Emphasized (!!!, capitals, repeated)
        - 1.8: Emotional content or identity
        - 2.0+: Explicit memory marker ("don't forget", "remember")
        """
        importance = 1.0

        # Make lowercase for matching
        msg_lower = full_message.lower()
        cand_lower = candidate.lower()

        # Explicit memory markers (immediate permanence)
        memory_markers = [
            "don't forget", "dont forget", "remember that", "remember this",
            "important:", "note:", "keep in mind", "make sure you remember",
            "this is important", "pay attention"
        ]

        for marker in memory_markers:
            if marker in msg_lower:
                importance = max(importance, 2.0)

        # Emotional content (create immediately)
        emotional_keywords = [
            "happy", "sad", "excited", "worried", "anxious", "proud", "grateful",
            "love", "hate", "miss", "appreciate", "disappointed", "frustrated",
            "scared", "nervous", "relieved", "thrilled", "overwhelmed"
        ]

        for emotion in emotional_keywords:
            if emotion in msg_lower or emotion in cand_lower:
                importance = max(importance, 1.8)

        # Identity/relationship statements (create immediately)
        # Check CANDIDATE only, not full message (to avoid false positives)
        identity_patterns = [
            r'\bi\'?m\s+\w+',  # "I'm Dee", "I'm a Navy nuke"
            r'\bmy name is',
            r'\bi am\s+\w+',
            r'\byou know i\'?m',
            r'\bwe\'?re\s+\w+',  # "we're friends"
        ]

        for pattern in identity_patterns:
            if re.search(pattern, cand_lower):
                importance = max(importance, 1.8)
        
        # Emphasis signals
        if "!!!" in full_message or "!!!" in candidate:
            importance = max(importance, 1.5)
        
        # Multiple mentions in same message
        if msg_lower.count(cand_lower) > 1:
            importance = max(importance, 1.5)
        
        # ALL CAPS (excluding single words)
        caps_words = len([w for w in candidate.split() if w.isupper() and len(w) > 3])
        if caps_words >= 2:
            importance = max(importance, 1.5)
        
        # Corrections/clarifications
        correction_patterns = ["actually", "i meant", "correction", "to clarify", "let me rephrase"]
        for pattern in correction_patterns:
            if pattern in msg_lower:
                importance = max(importance, 1.8)
        
        return importance
    
    def _track_reinforcement(self, candidate: str) -> bool:
        """
        Track reinforcement for a candidate memory.
        Returns True if memory should be created now.
        """
        # Create hash for deduplication (normalize whitespace)
        content_hash = " ".join(candidate.split()).lower()
        
        current_time = datetime.now()
        
        if content_hash not in self.reinforcement_buffer:
            # First mention - start tracking
            self.reinforcement_buffer[content_hash] = {
                "original_text": candidate,
                "count": 1,
                "first_seen": current_time.isoformat(),
                "last_seen": current_time.isoformat()
            }
            return False
        else:
            # Subsequent mention - increment
            entry = self.reinforcement_buffer[content_hash]
            entry["count"] += 1
            entry["last_seen"] = current_time.isoformat()
            
            # Check if ready for permanence
            first_seen = datetime.fromisoformat(entry["first_seen"])
            days_since_first = (current_time - first_seen).total_seconds() / 86400
            
            # Criteria: 3+ mentions within 30 days
            if entry["count"] >= 3 and days_since_first <= 30:
                # Remove from buffer (now permanent)
                del self.reinforcement_buffer[content_hash]
                return True
        
        return False
    
    def _create_memory(self, content: str, importance: float = 1.0) -> int:
        """
        Create a permanent memory in the vector store.
        """
        # Extract entities
        entities = extract_entities(content)
        
        # Add to memory store
        memory_id = self.memory_store.add_memory(
            content=content,
            timestamp=datetime.now(),
            importance=importance,
            entities=entities
        )
        
        return memory_id
    
    def save_reinforcement_buffer(self):
        """Save reinforcement tracking to disk"""
        try:
            with open(self.reinforcement_path, 'w', encoding='utf-8') as f:
                json.dump(self.reinforcement_buffer, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MEMORY FORMATION] ERROR saving reinforcement buffer: {e}")
    
    def load_reinforcement_buffer(self):
        """Load reinforcement tracking from disk"""
        try:
            if self.reinforcement_path.exists():
                with open(self.reinforcement_path, 'r', encoding='utf-8') as f:
                    self.reinforcement_buffer = json.load(f)
        except Exception as e:
            print(f"[MEMORY FORMATION] ERROR loading reinforcement buffer: {e}")
            self.reinforcement_buffer = {}
    
    def cleanup_old_reinforcements(self, max_age_days: int = 30):
        """
        Clean up old reinforcement entries that haven't been mentioned again.
        Run periodically (daily maintenance).
        """
        current_time = datetime.now()
        to_remove = []
        
        for content_hash, entry in self.reinforcement_buffer.items():
            last_seen = datetime.fromisoformat(entry["last_seen"])
            age_days = (current_time - last_seen).total_seconds() / 86400
            
            if age_days > max_age_days:
                to_remove.append(content_hash)
        
        for content_hash in to_remove:
            del self.reinforcement_buffer[content_hash]
        
        if to_remove:
            print(f"[MEMORY FORMATION] Cleaned up {len(to_remove)} old reinforcement entries")
            self.save_reinforcement_buffer()

# Global instance
_formation_system = None

def get_formation_system():
    """Get or create global formation system instance"""
    global _formation_system
    if _formation_system is None:
        _formation_system = MemoryFormation()
    return _formation_system

def observe_interaction(user_message: str, aid_response: str = None):
    """Convenience function for observing interactions"""
    formation = get_formation_system()
    return formation.observe_interaction(user_message, aid_response)