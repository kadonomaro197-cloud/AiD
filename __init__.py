# memory_management/__init__.py
"""
Memory Management Package - New Architecture
Simplified imports for the new FAISS-based memory system.
"""

import os
import json
from datetime import datetime

print("[MEMORY_INIT] Loading new memory system...")

# =======================
# PHASE 1: Core utilities (no dependencies)
# =======================
from . import utils
from . import emotion

# =======================
# PHASE 2: Keep STM for short-term buffer
# =======================
from . import stm

# =======================
# PHASE 3: New memory system modules
# =======================
# These are the 4 new files we created
try:
    from . import memory_vector_store
    from . import scoring
    from . import formation
    from . import retrieval
    print("[MEMORY_INIT] ✓ New memory system loaded")
except ImportError as e:
    print(f"[MEMORY_INIT] ⚠ Warning: Could not load new memory modules: {e}")

# =======================
# BACKWARD COMPATIBILITY (optional - can be removed later)
# =======================
# Keep old modules available if they exist, but don't fail if missing
try:
    from . import semantic_retrieval
    print("[MEMORY_INIT] ✓ Semantic retrieval available (legacy)")
except ImportError:
    print("[MEMORY_INIT] ⚠ Semantic retrieval not available")

# =======================
# UNIFIED API - New System
# =======================
def add_memory(content, importance=1.0, entities=None):
    """
    Add a new memory to the vector store.
    
    Args:
        content: Memory text
        importance: Importance multiplier (1.0-2.5)
        entities: List of entities (auto-extracted if None)
    
    Returns:
        Memory ID
    """
    from .memory_vector_store import get_memory_store
    store = get_memory_store()
    return store.add_memory(content, importance=importance, entities=entities)

def retrieve_memories(query, top_k=15):
    """
    Retrieve relevant memories for a query.
    
    Args:
        query: Search query
        top_k: Number of memories to return
    
    Returns:
        List of memory dicts with scores
    """
    from .retrieval import retrieve_memories as retrieve
    return retrieve(query, top_k)

def observe_interaction(user_message, aid_response=None):
    """
    Observe a conversation interaction for memory formation.
    
    Args:
        user_message: User's message
        aid_response: AiD's response (optional)
    
    Returns:
        List of created memory IDs
    """
    from .formation import observe_interaction as observe
    return observe(user_message, aid_response)

def format_memories_for_context(memories):
    """
    Format memories for injection into prompt context.
    
    Args:
        memories: List of memory dicts
    
    Returns:
        Formatted string for prompt
    """
    from .retrieval import format_memories_for_context as format_mem
    return format_mem(memories)

def get_memory_stats():
    """Get statistics about the memory system"""
    from .memory_vector_store import get_memory_store
    store = get_memory_store()
    return store.get_stats()

# =======================
# STM Functions (keep for short-term buffer)
# =======================
def add_to_stm(role, content):
    """Add message to short-term memory buffer"""
    return stm.add_message(role, content)

def get_stm_window(limit=None):
    """Get recent messages from STM"""
    return stm.get_recent_messages(limit)

def clear_stm():
    """Clear short-term memory"""
    return stm.clear()

# =======================
# Emotion utilities
# =======================
def get_emotion(text):
    """Get emotion for text"""
    return emotion.assign_emotion(text)

print("[MEMORY_INIT] ✓ Memory package ready")