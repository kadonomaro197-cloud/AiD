from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import re
import os
import random
import uuid

class TopicThread:
    """
    A conversational thread that was started but not resolved.
    """
    def __init__(self, topic, initial_context, depth_reached):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.initial_context = initial_context  # What was said
        self.depth_reached = depth_reached  # shallow, moderate, deep
        self.status = "open"  # open, resolved, abandoned
        self.created_at = datetime.now()
        self.last_mentioned = datetime.now()
        self.user_interest_signals = []  # Signs of interest
        self.priority = self._calculate_priority()
    
    def _calculate_priority(self):
        """
        Calculate how important this thread is.
        High priority: emotional, personal, career, relationship topics
        Low priority: trivia, casual mentions
        """
        high_priority_keywords = [
            "career", "job", "relationship", "family", "health",
            "stressed", "worried", "excited", "scared", "dream"
        ]
        
        topic_lower = self.topic.lower()
        if any(kw in topic_lower for kw in high_priority_keywords):
            return "high"
        
        return "medium"

class TopicThreadManager:
    """
    Manages conversational threads across sessions.
    """
    
    def __init__(self):
        self.threads = {}  # thread_id: TopicThread
        self.load_threads()
    
    def detect_thread_start(self, message: str, conversation_depth: str) -> Optional[TopicThread]:
        """
        Detect if a new conversational thread is starting.
        
        Signals:
        - User mentions something important but vague
        - Conversation gets deep but is interrupted
        - User says "I'm thinking about X" but doesn't elaborate
        """
        
        # Pattern: "I'm thinking about X" (future consideration)
        thinking_patterns = [
            r"i'm thinking about (.+)",
            r"i've been considering (.+)",
            r"i might (.+)",
            r"not sure if i should (.+)"
        ]
        
        for pattern in thinking_patterns:
            match = re.search(pattern, message.lower())
            if match:
                topic = match.group(1).strip()
                
                # Create thread
                thread = TopicThread(
                    topic=topic,
                    initial_context=message,
                    depth_reached="shallow"
                )
                
                self.threads[thread.id] = thread
                return thread
        
        return None
    
    def detect_thread_interruption(self, last_messages: List[Dict]) -> Optional[str]:
        """
        Detect if an important conversation was interrupted.
        
        Pattern:
        User shares something important (depth moderate/deep)
        → AiD responds with follow-up question
        → User changes topic (interruption detected)
        """
        
        if len(last_messages) < 3:
            return None
        
        # Check last 3 messages
        user_1 = last_messages[-3]
        aid_1 = last_messages[-2]
        user_2 = last_messages[-1]
        
        # Was AiD asking a follow-up question?
        if "?" in aid_1['content']:
            # Did user change topic instead of answering?
            # (Simple heuristic: completely different keywords)
            aid_keywords = set(aid_1['content'].lower().split())
            user_keywords = set(user_2['content'].lower().split())
            
            overlap = aid_keywords & user_keywords
            
            # If less than 2 words in common, topic changed
            if len(overlap) < 2:
                # Thread was interrupted
                topic = self._extract_topic(user_1['content'])
                
                if topic:
                    thread = TopicThread(
                        topic=topic,
                        initial_context=user_1['content'],
                        depth_reached="moderate"
                    )
                    
                    self.threads[thread.id] = thread
                    return thread.id
        
        return None
    
    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract topic from message (simple version)."""
        # Simple heuristic: take first 5 words
        words = message.split()[:5]
        if words:
            return " ".join(words)
        return None
    
    def get_thread_to_revisit(self, context: Dict) -> Optional[TopicThread]:
        """
        Decide if now is a good time to bring up an old thread.
        
        Good timing:
        - Natural lull in conversation
        - User seems open/relaxed
        - Related topic comes up
        - 2-5 days since thread was opened
        """
        
        open_threads = [t for t in self.threads.values() if t.status == "open"]
        
        if not open_threads:
            return None
        
        # Sort by priority and age
        now = datetime.now()
        
        candidates = []
        for thread in open_threads:
            days_old = (now - thread.created_at).days
            
            # Good window: 2-7 days old
            if 2 <= days_old <= 7:
                # High priority threads = higher chance
                if thread.priority == "high":
                    candidates.append((thread, 0.3))  # 30% chance
                else:
                    candidates.append((thread, 0.1))  # 10% chance
        
        if not candidates:
            return None
        
        # Check context - don't interrupt if user is stressed
        if context.get('emotion') in ['anxiety', 'frustration', 'sadness']:
            return None
        
        # Random selection weighted by priority
        if random.random() < candidates[0][1]:  # Check first candidate's probability
            return candidates[0][0]
        
        return None
    
    def format_callback_message(self, thread: TopicThread) -> str:
        """
        Format a natural callback to this thread.
        """
        
        days_ago = (datetime.now() - thread.created_at).days
        
        templates_by_priority = {
            "high": [
                f"Been thinking about what you said {days_ago} days ago - about {thread.topic}. You had more time to work through it?",
                f"So, that thing about {thread.topic} you mentioned - still on your mind?",
                f"Quick check-in: how're you feeling about {thread.topic} now?",
            ],
            "medium": [
                f"Remember when you brought up {thread.topic}? Whatever came of that?",
                f"Circling back - you mentioned {thread.topic} the other day. Curious how that's going.",
            ]
        }
        
        templates = templates_by_priority.get(thread.priority, templates_by_priority["medium"])
        
        return random.choice(templates)
    
    def mark_resolved(self, thread_id: str):
        """Mark thread as resolved (conversation concluded naturally)."""
        if thread_id in self.threads:
            self.threads[thread_id].status = "resolved"
            self.save_threads()
    
    def get_open_threads(self) -> List[TopicThread]:
        """Get all open threads."""
        return [t for t in self.threads.values() if t.status == "open"]
    
    def load_threads(self):
        """Load threads from file."""
        try:
            filepath = "Persona/data/threads.json"
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Reconstruct threads from saved data
                    for thread_data in data:
                        thread = TopicThread(
                            topic=thread_data['topic'],
                            initial_context=thread_data['initial_context'],
                            depth_reached=thread_data['depth_reached']
                        )
                        thread.id = thread_data['id']
                        thread.status = thread_data['status']
                        thread.created_at = datetime.fromisoformat(thread_data['created_at'])
                        thread.last_mentioned = datetime.fromisoformat(thread_data['last_mentioned'])
                        self.threads[thread.id] = thread
        except Exception as e:
            print(f"[THREADING] Error loading threads: {e}")
    
    def save_threads(self):
        """Save threads to file."""
        try:
            os.makedirs("Persona/data", exist_ok=True)
            filepath = "Persona/data/threads.json"
            
            data = []
            for thread in self.threads.values():
                data.append({
                    'id': thread.id,
                    'topic': thread.topic,
                    'initial_context': thread.initial_context,
                    'depth_reached': thread.depth_reached,
                    'status': thread.status,
                    'created_at': thread.created_at.isoformat(),
                    'last_mentioned': thread.last_mentioned.isoformat(),
                    'priority': thread.priority
                })
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[THREADING] Error saving threads: {e}")

# =======================
# GLOBAL INSTANCE
# =======================
_thread_manager = None

def init_topic_threading():
    """Initialize topic threading system."""
    global _thread_manager
    _thread_manager = TopicThreadManager()
    print("[THREADING] ✓ Topic threading initialized")

def detect_thread_start(message: str, conversation_depth: str) -> Optional[TopicThread]:
    """Detect if new thread is starting."""
    if _thread_manager:
        return _thread_manager.detect_thread_start(message, conversation_depth)
    return None

def detect_thread_interruption(last_messages: List[Dict]) -> Optional[str]:
    """Detect if thread was interrupted."""
    if _thread_manager:
        return _thread_manager.detect_thread_interruption(last_messages)
    return None

def get_thread_to_revisit(context: Dict) -> Optional[TopicThread]:
    """Get thread to bring up."""
    if _thread_manager:
        return _thread_manager.get_thread_to_revisit(context)
    return None

def get_open_threads() -> List[TopicThread]:
    """Get all open threads."""
    if _thread_manager:
        return _thread_manager.get_open_threads()
    return []