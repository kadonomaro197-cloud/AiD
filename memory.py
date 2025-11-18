# memory.py
"""
AID Memory Management System - RTX 3090 24GB / CYDONIA-24B OPTIMIZED
Handles sliding context windows, mode-specific allocation, and memory retrieval.

ARCHITECTURE:
- STM: Persistent storage across sessions (200 messages, disk-backed) [UPGRADED]
- Runtime: Live conversation buffer (grows during session, memory-only) [EXPANDED]
- Sliding Window: TIME-BASED multi-tier system (Recent/Medium/Archive)
- Modes: CHAT, MEMORY, RAG with different token allocations [32K CONTEXT]
- Chat Format: Cydonia native format [INST]/[/INST] [UPGRADED]
- NEW: FAISS-based memory system with scoring and formation
"""

import json
import re
import threading
import time
from datetime import datetime, timedelta

# Memory imports
from memory_management import stm as mem_stm
from memory_management import emotion as mem_emotion
from memory_management import utils as mem_utils
from Persona import relationship

# =======================
# MODE DEFINITIONS
# =======================
class AIDMode:
    CHAT = "chat"
    MEMORY = "memory"
    RAG = "rag"

# =======================
# AUTO-SAVE CONFIGURATION
# =======================
_auto_save_thread = None
_auto_save_running = False
AUTO_SAVE_INTERVAL = 60  # Save runtime to STM every 60 seconds

# =======================
# TOKEN BUDGETS PER MODE (RTX 3090 24GB - 32K CONTEXT OPTIMIZED)
# =======================
MODE_BUDGETS = {
    AIDMode.CHAT: {
        "system": 400,           # 2x increase - more personality depth
        "relationship": 200,     # 2x increase - richer relationship context
        "examples": 0,
        "world_info": 3000,      # INCREASED: For new memory system
        "recent": 15000,         # 5x increase - leverage that 32k window!
        "response": 1500,
        "total_budget": 28000    # Use 28k of 32k (leave 4k for response)
    },
    AIDMode.MEMORY: {
        "system": 300,           # 2x increase
        "relationship": 0,
        "examples": 0,
        "world_info": 3500,      # INCREASED: For memory-focused queries
        "recent": 10000,         # 5x increase
        "response": 1500,
        "total_budget": 28000
    },
    AIDMode.RAG: {
        "system": 300,           # 2x increase
        "relationship": 0,
        "examples": 0,
        "world_info": 12000,     # 6x increase - deep research capability
        "recent": 6000,          # 4x increase
        "response": 2000,
        "total_budget": 28000
    }
}

# =======================
# PERSONALITY VARIANTS (CONDENSED)
# =======================

# Import personality system
from Persona import personality

# Use personality.build_personality_prompt() instead of hardcoded text

# =======================
# RUNTIME CONVERSATION STATE (UPGRADED FOR 32K)
# =======================
_runtime_conversation = []
_runtime_lock = threading.Lock()

def add_to_runtime(role: str, content: str, emotion: str = "neutral"):
    """Add message to runtime with safeguards against memory leaks."""
    global _runtime_conversation
    
    MAX_SINGLE_MESSAGE_TOKENS = 8000  # UPGRADED: 8000 from 1500 for 32k context
    token_estimate = estimate_tokens(content)
    
    if token_estimate > MAX_SINGLE_MESSAGE_TOKENS:
        print(f"[MEMORY] Message too large ({token_estimate} tokens), skipping runtime")
        return
    
    with _runtime_lock:
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion
        }
        _runtime_conversation.append(entry)
        
        # PERIODIC CLEANUP - Every 100 messages
        if len(_runtime_conversation) % 100 == 0:
            periodic_runtime_cleanup()

def periodic_runtime_cleanup():
    """Periodically clean runtime buffer - call this every 100 messages."""
    global _runtime_conversation
    MAX_RUNTIME_SIZE = 1000  # UPGRADED: 1000 from 200 for deeper context
    
    with _runtime_lock:
        if len(_runtime_conversation) > MAX_RUNTIME_SIZE:
            excess = len(_runtime_conversation) - MAX_RUNTIME_SIZE
            _runtime_conversation = _runtime_conversation[excess:]
            print(f"[MEMORY] [CLEANUP] Trimmed {excess} messages from runtime buffer")

def get_runtime_messages():
    """Get all runtime messages."""
    with _runtime_lock:
        return list(_runtime_conversation)

def get_runtime_size():
    """Get number of messages in runtime."""
    with _runtime_lock:
        return len(_runtime_conversation)

def clear_runtime():
    """Clear runtime conversation buffer."""
    global _runtime_conversation
    with _runtime_lock:
        _runtime_conversation = []
    print("[MEMORY] Runtime buffer cleared")

# =======================
# INITIALIZATION
# =======================
def init_runtime_from_stm():
    """Load STM into runtime on startup."""
    global _runtime_conversation
    stm_messages = mem_stm.get_all()
    
    with _runtime_lock:
        _runtime_conversation = list(stm_messages)
    
    print(f"[MEMORY] Loaded {len(stm_messages)} messages from STM into runtime buffer")

def cleanup_runtime():
    """Remove oversized messages from runtime on startup."""
    global _runtime_conversation
    MAX_NORMAL_MESSAGE_TOKENS = 500
    
    with _runtime_lock:
        cleaned = []
        removed_count = 0
        
        for msg in _runtime_conversation:
            content = msg.get('content', '')
            token_estimate = len(content.split()) * 1.3
            
            if token_estimate > MAX_NORMAL_MESSAGE_TOKENS:
                removed_count += 1
                print(f"[MEMORY] [CLEANUP] Removed oversized message ({int(token_estimate)} tokens)")
            else:
                cleaned.append(msg)
        
        _runtime_conversation = cleaned
        
        if removed_count > 0:
            print(f"[MEMORY] [CLEANUP] Removed {removed_count} oversized messages")
        else:
            print(f"[MEMORY] [CLEANUP] Runtime clean - {len(_runtime_conversation)} normal messages")

def _auto_save_loop():
    """Background thread that periodically saves runtime to STM."""
    global _auto_save_running, _runtime_conversation, _runtime_lock
    print("[MEMORY] Auto-save loop thread started")
    
    while _auto_save_running:
        time.sleep(AUTO_SAVE_INTERVAL)
        if not _auto_save_running:
            break
        try:
            # Copy data while holding lock, then release BEFORE disk I/O
            with _runtime_lock:
                # UPGRADED: Save last 200 messages instead of 50
                messages_to_save = _runtime_conversation[-200:] if len(_runtime_conversation) > 200 else _runtime_conversation
                # Make a deep copy to avoid holding lock during I/O
                messages_copy = list(messages_to_save)
                saved_count = len(messages_copy)

            # Disk I/O happens OUTSIDE the lock to avoid blocking other operations
            import memory_management.stm as mem_stm_module
            mem_stm_module._stm_data = messages_copy
            mem_stm.save_stm(log=False)

            print(f"[MEMORY] [AUTO-SAVE] Saved {saved_count} messages to STM")
        except Exception as e:
            print(f"[MEMORY] [AUTO-SAVE] Failed: {e}")
            import traceback
            traceback.print_exc()

def start_auto_save_loop():
    """Start the auto-save background thread."""
    global _auto_save_thread, _auto_save_running
    
    if _auto_save_thread is not None and _auto_save_thread.is_alive():
        print("[MEMORY] Auto-save loop already running")
        return
    
    _auto_save_running = True
    _auto_save_thread = threading.Thread(target=_auto_save_loop, daemon=True)
    _auto_save_thread.start()
    print(f"[MEMORY] [OK] Auto-save enabled: Runtime -> STM every {AUTO_SAVE_INTERVAL} seconds")

def stop_auto_save_loop():
    """Stop the auto-save background thread."""
    global _auto_save_running
    _auto_save_running = False
    if _auto_save_thread is not None:
        print("[MEMORY] Auto-save loop stopped")

# =======================
# TOKEN ESTIMATION
# =======================
def estimate_tokens(text: str) -> int:
    """Estimate token count (1 token ≈ 0.75 words)."""
    if not text:
        return 0
    words = len(text.split())
    return int(words * 1.3)

def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to fit token budget."""
    if estimate_tokens(text) <= max_tokens:
        return text
    
    target_words = int(max_tokens / 1.3)
    words = text.split()
    if len(words) <= target_words:
        return text
    
    return ' '.join(words[:target_words]) + "..."

# =======================
# SLIDING WINDOW (TIME-BASED)
# =======================
def build_sliding_window(mode: str, token_budget: int, runtime_messages: list) -> dict:
    """
    Build time-based sliding window with tier allocation.
    
    TIER SYSTEM (UPGRADED FOR 32K):
    - Recent (Last 30 min): 60% of tokens
    - Medium (30 min - 6 hours): 25% of tokens
    - Archive (6+ hours ago): 15% of tokens
    """
    
    if not runtime_messages:
        return {"text": "", "tier_breakdown": {"recent": 0, "medium": 0, "archive": 0}}
    
    now = datetime.now()
    
    # Time boundaries
    recent_cutoff = now - timedelta(minutes=30)
    medium_cutoff = now - timedelta(hours=6)
    
    # Sort messages by timestamp
    sorted_messages = sorted(
        runtime_messages,
        key=lambda m: m.get('timestamp', ''),
        reverse=False
    )
    
    # Categorize messages
    recent_msgs = []
    medium_msgs = []
    archive_msgs = []
    
    for msg in sorted_messages:
        try:
            timestamp = datetime.fromisoformat(msg.get('timestamp', ''))
            if timestamp >= recent_cutoff:
                recent_msgs.append(msg)
            elif timestamp >= medium_cutoff:
                medium_msgs.append(msg)
            else:
                archive_msgs.append(msg)
        except:
            recent_msgs.append(msg)
    
    # Token allocation per tier (OPTIMIZED FOR 32K)
    recent_budget = int(token_budget * 0.60)  # 60%
    medium_budget = int(token_budget * 0.25)  # 25%
    archive_budget = int(token_budget * 0.15) # 15%
    
    # Build context sections
    def format_tier(messages, budget, tier_name):
        if not messages:
            return ""
        
        lines = [f"[{tier_name.upper()}]"]
        used_tokens = 0
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            prefix = 'user' if role == 'user' else 'aid'
            
            msg_text = f"{prefix}: {content}"
            msg_tokens = estimate_tokens(msg_text)
            
            if used_tokens + msg_tokens > budget:
                break
            
            lines.append(msg_text)
            used_tokens += msg_tokens
        
        return "\n".join(lines)
    
    sections = []
    
    archive_text = format_tier(archive_msgs, archive_budget, "Archive")
    if archive_text:
        sections.append(archive_text)
    
    medium_text = format_tier(medium_msgs, medium_budget, "Medium")
    if medium_text:
        sections.append(medium_text)
    
    recent_text = format_tier(recent_msgs, recent_budget, "Recent")
    if recent_text:
        sections.append(recent_text)
    
    return {
        "text": "\n\n".join(sections),
        "tier_breakdown": {
            "recent": len(recent_msgs),
            "medium": len(medium_msgs),
            "archive": len(archive_msgs)
        }
    }

# =======================
# MODE DETECTION
# =======================
def detect_mode(user_message: str, rag_context: str, memory_context: str) -> str:
    """Detect conversation mode based on context."""
    user_lower = user_message.lower()
    
    # RAG mode
    if rag_context:
        return AIDMode.RAG
    
    # MEMORY mode
    memory_keywords = [
        'remember', 'recall', 'what did', 'when did', 'have we',
        'do you remember', 'you said', 'i told you', 'we talked about'
    ]
    if any(kw in user_lower for kw in memory_keywords) or memory_context:
        return AIDMode.MEMORY
    
    # Default to CHAT
    return AIDMode.CHAT

# =======================
# MAIN BUILD PROMPT FUNCTION (CYDONIA FORMAT WITH NEW MEMORY SYSTEM)
# =======================
def build_prompt(user_message: str, rag_context: str = "", memory_context: str = "", force_mode: str = None) -> dict:
    """
    Build complete prompt with context layers using Cydonia native format.
    
    NEW: Accepts memory_context from the new FAISS-based memory system.
    This context is injected into world_info section for model to use naturally.
    
    Returns dict with prompt, mode, and metadata.
    """
    
    # === EXISTING CODE: Get runtime messages ===
    runtime_messages = get_runtime_messages()
    
    # Detect mode
    mode = force_mode if force_mode else detect_mode(user_message, rag_context, memory_context)
    budget = MODE_BUDGETS[mode]
    
    # === OLD PERSISTENT MEMORY SYSTEM (OPTIONAL - Can be removed after testing) ===
    # Commenting out for now - new memory system replaces this
    # If you want to run both systems in parallel during testing, uncomment these lines
    """
    from memory_management import persistent as mem_persist
    from memory_management import retrieval as mem_retrieval
    
    # Step 1: Decay existing memories
    mem_persist.decay_memories(user_message)
    
    # Step 2: Auto-scan for new relevant memories
    auto_scanned = mem_retrieval.auto_scan_memories(user_message, top_k=3)
    
    # Step 3: Activate any newly found memories
    for mem in auto_scanned:
        mem_persist.activate_memory(mem, initial_strength=1.0, priority="auto")
    
    # Step 4: Get formatted active memories for context
    persistent_memories = mem_persist.get_active_memories(token_budget=budget["world_info"] // 2)
    """
    persistent_memories = []  # Disabled old system
    
    print(f"\n{'='*60}")
    print(f"[MODE] {mode.upper()}")
    print(f"[BUDGET] Total prompt budget: {budget['total_budget']} tokens")
    print(f"{'='*60}")
    
    # === BUILD PROMPT LAYERS (CYDONIA NATIVE FORMAT) ===
    prompt_parts = []
    
    # LAYER 1: System message
    prompt_parts.append("[SYSTEM_PROMPT]")
    
    system_content = []
    
    # System personality
    system_text = personality.build_personality_prompt(mode=mode, include_system_awareness=False)
    system_truncated = truncate_to_tokens(system_text, budget["system"])
    system_content.append(system_truncated)
    
    # Relationship context (CHAT only)
    rel_truncated = ""
    if budget["relationship"] > 0 and mode == AIDMode.CHAT:
        rel_context = relationship.get_relationship_context()
        rel_truncated = truncate_to_tokens(rel_context, budget["relationship"])
        system_content.append(f"\n{rel_truncated}")
    
    # World info (RAG, Memory, NEW Memory System)
    world_info_parts = []
    
    if mode == AIDMode.RAG and rag_context:
        world_info_parts.append(f"[Database Results]\n{rag_context}")
    
    # === NEW: Inject memory context from FAISS-based memory system ===
    if memory_context:
        # Memory context comes pre-formatted from format_memories_for_context()
        world_info_parts.append(f"[Relevant Memories]\n{memory_context}")
        print(f"[NEW MEMORY] Injected {estimate_tokens(memory_context)} tokens of memory context")
    
    # Old persistent memories (if running in parallel)
    if persistent_memories:
        persistent_text = "\n\n".join(persistent_memories)
        world_info_parts.append(f"[Active Context]\n{persistent_text}")
    
    world_info_text = "\n\n".join(world_info_parts)
    
    if world_info_text and budget["world_info"] > 0:
        world_truncated = truncate_to_tokens(world_info_text, budget["world_info"])
        system_content.append(f"\n{world_truncated}")
    
    prompt_parts.append("\n".join(system_content))
    prompt_parts.append("[/SYSTEM_PROMPT]")
    
    # LAYER 2: Sliding window context (Cydonia format)
    sliding_window = build_sliding_window(mode, budget["recent"], runtime_messages)
    
    if sliding_window["text"]:
        lines = sliding_window["text"].split('\n')
        current_role = None
        current_content = []
        
        for line in lines:
            if line.startswith('[') and line.endswith(']'):
                continue
            
            if line.startswith('user:') or line.startswith('aid:'):
                # Close previous message
                if current_role and current_content:
                    content_text = "\n".join(current_content)
                    if current_role == 'user':
                        prompt_parts.append(f"[INST]{content_text}[/INST]")
                    else:
                        prompt_parts.append(f"{content_text}</s>")
                
                # Start new message
                role = 'user' if line.startswith('user:') else 'assistant'
                current_role = role
                current_content = [line.split(':', 1)[1].strip()]
            elif line.strip() and current_role:
                current_content.append(line)
        
        # Close final message
        if current_role and current_content:
            content_text = "\n".join(current_content)
            if current_role == 'user':
                prompt_parts.append(f"[INST]{content_text}[/INST]")
            else:
                prompt_parts.append(f"{content_text}</s>")
    
    # LAYER 3: Current user message
    prompt_parts.append(f"[INST]{user_message}[/INST]")
    
    # Note: Assistant response starts immediately after [/INST], no prefix needed
    
    final_prompt = "\n".join(prompt_parts)
    final_tokens = estimate_tokens(final_prompt)
    
    # Token breakdown
    token_breakdown = {
        "system": estimate_tokens(system_truncated),
        "relationship": estimate_tokens(rel_truncated) if rel_truncated else 0,
        "world_info": estimate_tokens(world_info_text) if world_info_text else 0,
        "recent_chat": estimate_tokens(sliding_window["text"]),
        "total": final_tokens,
        "budget": budget["total_budget"],
        "over_budget": final_tokens > budget["total_budget"]
    }
    
    # Logging
    print(f"[RUNTIME] Buffer size: {get_runtime_size()} messages")
    print(f"[WINDOW] Sliding window tiers (TIME-BASED):")
    for tier, count in sliding_window['tier_breakdown'].items():
        print(f"   |- {tier.capitalize()}: {count} messages")
    print(f"[TOKENS] Breakdown:")
    print(f"   |- System: {token_breakdown['system']}")
    if token_breakdown['relationship'] > 0:
        print(f"   |- Relationship: {token_breakdown['relationship']}")
    print(f"   |- World Info: {token_breakdown['world_info']}")
    print(f"   |- Recent Chat: {token_breakdown['recent_chat']}")
    print(f"   |- TOTAL: {token_breakdown['total']} / {token_breakdown['budget']}")
    
    if token_breakdown['over_budget']:
        print(f"   ⚠️ OVER BUDGET by {token_breakdown['total'] - token_breakdown['budget']} tokens!")
    else:
        headroom = token_breakdown['budget'] - token_breakdown['total']
        print(f"   ✓ {headroom} tokens headroom")
    
    return {
        "prompt": final_prompt,
        "mode": mode,
        "token_breakdown": token_breakdown,
        "max_response_tokens": budget["response"],
        "sliding_window_tiers": sliding_window['tier_breakdown'],
        "runtime_total": get_runtime_size()
    }

# =======================
# SAMPLING PARAMETERS (CYDONIA-OPTIMIZED)
# =======================
def get_sampling_params(mode: str, total_tokens: int) -> dict:
    """
    Get Cydonia-optimized sampling parameters.
    
    Cydonia-24B performs best with:
    - temperature: 0.7-1.0 (higher for creativity)
    - min_p: 0.05-0.10 (better than top_p for Cydonia)
    - repetition_penalty: 1.05-1.15
    """
    
    if mode == AIDMode.CHAT:
        return {
            "temperature": 0.65,     # Reduced from 0.85 to prevent hallucinations
            "min_p": 0.08,           # Cydonia prefers min_p over top_p
            "top_k": 50,
            "repetition_penalty": 1.10,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1
        }
    elif mode == AIDMode.MEMORY:
        return {
            "temperature": 0.55,     # Reduced from 0.75 to prevent hallucinations in memory mode
            "min_p": 0.05,
            "top_k": 40,
            "repetition_penalty": 1.08,
            "presence_penalty": 0.05,
            "frequency_penalty": 0.05
        }
    else:  # RAG
        return {
            "temperature": 0.70,
            "min_p": 0.05,
            "top_k": 35,
            "repetition_penalty": 1.05,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0
        }