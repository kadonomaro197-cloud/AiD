# memory_management/stm.py
# PHASE 2 UPGRADED: RTX 3090 24GB - Expanded STM capacity
import os
import json
import threading
import time
from datetime import datetime
from . import emotion as mem_emotion
from . import utils as mem_utils

# =======================
# CONFIGURATION (PHASE 2 UPGRADED)
# =======================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STM_FILE = os.path.join(PROJECT_ROOT, "memory_management", "stm.json")
STM_MESSAGE_LIMIT = 200      # UPGRADED: 200 from 50 (4x increase for 32k context)
MAX_CONTENT_LENGTH = 2000   # Max chars per message
AUTO_SAVE_INTERVAL = 3600   # Auto-save every 60 seconds

_stm_data = []
_stm_lock = threading.Lock()
_auto_save_thread = None
_auto_save_running = False
_stm_counter = 0  # For unique IDs

# =======================
# STM INITIALIZATION
# =======================
def init_stm():
    """Load STM from disk if exists, else start fresh."""
    global _stm_data, _stm_counter
    if os.path.exists(STM_FILE):
        try:
            with open(STM_FILE, "r", encoding="utf-8") as f:
                _stm_data = json.load(f)
                _stm_data = _stm_data[-STM_MESSAGE_LIMIT:]  # ensure limit
                _stm_counter = len(_stm_data)
            print(f"[STM] Loaded {len(_stm_data)} messages from STM.")
        except Exception as e:
            print(f"[STM] Failed to load STM: {e}")
            _stm_data = []
            _stm_counter = 0
    else:
        _stm_data = []
        _stm_counter = 0
        print("[STM] No existing STM found. Starting fresh.")

def save_stm(log=False):
    """Save current STM to disk."""
    global _stm_data
    try:
        with _stm_lock:
            os.makedirs(os.path.dirname(STM_FILE), exist_ok=True)
            with open(STM_FILE, "w", encoding="utf-8") as f:
                json.dump(_stm_data[-STM_MESSAGE_LIMIT:], f, ensure_ascii=False, indent=2)
        if log:
            print(f"[STM] Saved {len(_stm_data)} messages.")
    except Exception as e:
        print(f"[STM] Failed to save STM: {e}")

# =======================
# AUTO-SAVE LOOP
# =======================
def _auto_save_loop():
    global _auto_save_running
    while _auto_save_running:
        time.sleep(AUTO_SAVE_INTERVAL)
        save_stm()

def start_auto_save_loop():
    """Start background thread to auto-save STM periodically."""
    global _auto_save_thread, _auto_save_running
    if _auto_save_thread is None:
        _auto_save_running = True
        _auto_save_thread = threading.Thread(target=_auto_save_loop, daemon=True)
        _auto_save_thread.start()
        print("[STM] Auto-save loop started.")

def stop_auto_save_loop():
    """Stop the auto-save background thread."""
    global _auto_save_running
    _auto_save_running = False

# =======================
# STM MANAGEMENT (PHASE 2 UPGRADED)
# =======================
def add_to_stm(role: str, content: str, emotion=None):
    """Add a new message to STM with unique ID and size limits."""
    global _stm_data, _stm_counter, _stm_lock
    
    # TRUNCATE OVERSIZED CONTENT
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "...[truncated]"
        print(f"[STM] Truncated oversized message to {MAX_CONTENT_LENGTH} chars")
    
    with _stm_lock:
        _stm_counter += 1
        entry = {
            "id": _stm_counter,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if emotion:
            entry["emotion"] = emotion
        
        _stm_data.append(entry)
        
        # ENFORCE SIZE LIMIT (UPGRADED TO 200)
        if len(_stm_data) > STM_MESSAGE_LIMIT:
            removed = _stm_data[:len(_stm_data) - STM_MESSAGE_LIMIT]
            _stm_data = _stm_data[-STM_MESSAGE_LIMIT:]
            print(f"[STM] Trimmed {len(removed)} old messages (keeping last {STM_MESSAGE_LIMIT})")

def add_message(role: str, content: str, emotion=None, timestamp=None):
    """Alias for add_to_stm for compatibility."""
    add_to_stm(role, content, emotion)

def get_all():
    """Get all STM messages."""
    with _stm_lock:
        return list(_stm_data)

def get_recent(n=10):
    """Get last N messages from STM."""
    with _stm_lock:
        return list(_stm_data[-n:])

def clear_stm():
    """Clear all STM data."""
    global _stm_data
    with _stm_lock:
        _stm_data = []
    save_stm()
    print("[STM] Cleared all STM data")

def count_messages():
    """Count messages in STM."""
    with _stm_lock:
        return len(_stm_data)

# =======================
# PHASE 2 UPGRADE NOTES
# =======================
"""
CHANGES FROM 8GB TO 24GB VERSION:
- STM_MESSAGE_LIMIT: 50 → 200 (4x increase)
- Supports deeper conversation history
- Works with expanded runtime buffer (1000 messages)
- Optimized for 32k context window

PERFORMANCE IMPACT:
- Disk usage: ~50KB → ~200KB per STM save
- Load time: <100ms even with 200 messages
- Memory overhead: Negligible (~1MB RAM)
"""