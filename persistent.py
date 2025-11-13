# memory_management/persistent.py
"""
Persistent Memory System - Keeps memories active across multiple turns.
Memories fade naturally when not referenced, can be reinforced when mentioned.
"""

import threading
from datetime import datetime

# =======================
# ACTIVE MEMORY POOL
# =======================
_active_memories = []  # List of active memory objects
_memory_lock = threading.Lock()

# =======================
# CONFIGURATION
# =======================
DECAY_RATE = 0.15           # Strength lost per turn (15%)
MIN_STRENGTH = 0.05         # Remove when below this
REINFORCEMENT_BOOST = 0.4   # Strength gained when mentioned again
MAX_ACTIVE = 5              # Max memories active at once


# =======================
# CORE FUNCTIONS
# =======================

def activate_memory(memory_entry: dict, initial_strength: float = 1.0, priority: str = "auto"):
    """
    Add memory with priority and conflict resolution.
    priority: "manual" (user-selected) or "auto" (keyword-activated)
    """
    with _memory_lock:
        mem_id = memory_entry.get("id", "unknown")
        keywords = extract_keywords(memory_entry)
        
        # Check if already active
        for active in _active_memories:
            if active["id"] == mem_id:
                # Upgrade if manual
                if priority == "manual":
                    active["priority"] = "manual"
                    active["strength"] = 1.0
                    print(f"[PERSIST] Upgraded {mem_id} to manual priority")
                else:
                    active["strength"] = min(1.0, active["strength"] + REINFORCEMENT_BOOST)
                active["last_referenced"] = datetime.now()
                return
        
        # If manual, clear conflicting memories
        if priority == "manual":
            for active in _active_memories[:]:
                active_keywords = active.get("keywords", [])
                overlap = set(keywords) & set(active_keywords)
                
                # Significant overlap (>50% keywords match) = conflict
                if len(overlap) > len(keywords) * 0.5:
                    _active_memories.remove(active)
                    print(f"[PERSIST] Cleared conflicting memory: {active['id']}")
        
        # Add new memory
        _active_memories.append({
            "id": mem_id,
            "title": memory_entry.get("title", "Untitled"),
            "content": memory_entry.get("content", ""),
            "summary": memory_entry.get("corrected_summary") or memory_entry.get("summary", ""),
            "strength": initial_strength,
            "priority": priority,
            "activated_at": datetime.now(),
            "last_referenced": datetime.now(),
            "keywords": keywords
        })
        
        print(f"[PERSIST] Activated {mem_id} (priority: {priority}, strength: {initial_strength:.2f})")
        
        # Enforce max active
        if len(_active_memories) > MAX_ACTIVE:
            # Remove weakest AUTO memory (never remove manual)
            auto_mems = [m for m in _active_memories if m.get("priority") != "manual"]
            if auto_mems:
                auto_mems.sort(key=lambda m: m["strength"])
                removed = auto_mems[0]
                _active_memories.remove(removed)
                print(f"[PERSIST] Removed weakest auto memory: {removed['id']}")


def decay_memories(current_message: str):
    """
    Reduce strength of all active memories.
    Remove memories below minimum strength.
    Reinforce memories mentioned in current message.
    """
    with _memory_lock:
        msg_lower = current_message.lower()
        
        for mem in _active_memories[:]:  # Copy to allow removal during iteration
            # Check if memory keywords appear in message
            is_relevant = any(kw.lower() in msg_lower for kw in mem.get("keywords", []))
            
            if is_relevant:
                # Reinforce
                mem["strength"] = min(1.0, mem["strength"] + REINFORCEMENT_BOOST)
                mem["last_referenced"] = datetime.now()
                print(f"[PERSIST] Reinforced: {mem['id']} (strength: {mem['strength']:.2f})")
            else:
                # Decay
                old_strength = mem["strength"]
                mem["strength"] *= (1 - DECAY_RATE)
                
                # Remove if too weak
                if mem["strength"] < MIN_STRENGTH:
                    _active_memories.remove(mem)
                    print(f"[PERSIST] Forgot: {mem['id']} (strength: {mem['strength']:.2f})")


def get_active_memories(token_budget: int = 3000) -> list:
    """
    Return memories sorted by priority (manual first) then strength.
    Format based on strength (stronger = more detail).
    """
    with _memory_lock:
        if not _active_memories:
            return []
        
        # Sort: manual first, then by strength
        def sort_key(m):
            priority_score = 1000 if m.get("priority") == "manual" else 0
            return priority_score + m["strength"]
        
        sorted_mems = sorted(_active_memories, key=sort_key, reverse=True)
        
        formatted = []
        used_tokens = 0
        
        for mem in sorted_mems:
            strength = mem["strength"]
            is_manual = mem.get("priority") == "manual"
            
            # Manual = full detail always
            if is_manual:
                content = mem["content"]
                header = f"[{mem['title']}] (user requested)"
            elif strength > 0.7:
                content = mem["content"]
                header = f"[{mem['title']}] (clear memory)"
            elif strength > 0.4:
                content = mem["summary"]
                header = f"[{mem['title']}] (fading)"
            else:
                content = mem["summary"][:150] + "..."
                header = f"[{mem['title']}] (vague)"
            
            text = f"{header}\n{content}"
            tokens = estimate_tokens(text)
            
            # Manual memories bypass budget (force them in)
            if used_tokens + tokens > token_budget and not is_manual:
                break
            
            formatted.append(text)
            used_tokens += tokens
        
        return formatted


def clear_all_memories():
    """Clear all active memories (for testing/reset)."""
    with _memory_lock:
        count = len(_active_memories)
        _active_memories.clear()
        print(f"[PERSIST] Cleared {count} active memories")


def get_memory_status() -> dict:
    """Return status info about active memories."""
    with _memory_lock:
        return {
            "active_count": len(_active_memories),
            "memories": [
                {
                    "id": m["id"],
                    "title": m["title"],
                    "strength": round(m["strength"], 2),
                    "priority": m.get("priority", "auto"),
                    "age_seconds": (datetime.now() - m["activated_at"]).total_seconds()
                }
                for m in _active_memories
            ]
        }


# =======================
# HELPER FUNCTIONS
# =======================

def extract_keywords(memory_entry: dict) -> list:
    """
    Extract keywords from memory for relevance checking.
    Uses title, tags, and category.
    """
    keywords = []
    
    # From title
    title = memory_entry.get("title", "")
    if title:
        keywords.extend(title.split())
    
    # From tags
    tags = memory_entry.get("tags", [])
    keywords.extend(tags)
    
    # From category path
    category = memory_entry.get("category_path", [])
    if isinstance(category, list):
        keywords.extend(category)
    elif isinstance(category, str):
        keywords.extend(category.split("/"))
    
    # Clean and deduplicate
    keywords = list(set(k.strip().lower() for k in keywords if k and len(k) > 2))
    
    return keywords


def estimate_tokens(text: str) -> int:
    """Estimate token count (same as memory.py)."""
    if not text:
        return 0
    return int(len(text.split()) * 1.5)