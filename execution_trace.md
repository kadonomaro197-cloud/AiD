# Execution Trace: "Hi AiD" Message Flow

## Step-by-Step Simulation

### 1. Discord Event Received
**File:** discord.py (library)
- Discord receives message "Hi AiD" from user
- Triggers `on_message` event

---

### 2. auto_response.py - Message Handler Entry
**File:** auto_response.py, Line 194-195
```python
async def _on_message(message):
    print(f"[AUTO_RESPONSE] on_message triggered for message: {message.content[:50]}")
```
**Log:** `[AUTO_RESPONSE] on_message triggered for message: Hey AiD` ✅ SEEN

---

### 3. Bot Self-Message Check
**File:** auto_response.py, Line 200-201
```python
if message.author == bot.user:
    return
```
**Result:** PASS (message is from user, not bot)

---

### 4. Command Prefix Check
**File:** auto_response.py, Line 204-209
```python
if message.content.strip().startswith("!"):
    await bot.process_commands(message)
    return
```
**Result:** PASS ("Hi AiD" doesn't start with "!")

---

### 5. Process Commands (Legacy)
**File:** auto_response.py, Line 222-228
```python
try:
    await bot.process_commands(message)
except Exception:
    traceback.print_exc()
```
**Result:** Runs but does nothing (no command to process)

---

### 6. Variable Initialization
**File:** auto_response.py, Line 233-235
```python
content = message.content.strip()  # "Hey AiD"
loop = asyncio.get_event_loop()
reply = None
```
**Debug Logs:**
- `[DEBUG] Interactive mode: False` ✅ SEEN
- `[DEBUG] Pending memory context type: <class 'NoneType'>` ✅ SEEN
- `[DEBUG] Content: 'Hey AiD' | isdigit: False` ✅ SEEN

---

### 7. Trigger Detection
**File:** auto_response.py, Line 358-511
- Line 358: `print(f"[AUTO_RESPONSE] Checking message triggers for: {content[:50]}")`
  **Log:** `[AUTO_RESPONSE] Checking message triggers for: Hey AiD` ✅ SEEN
- Line 360: Check "aid create a memory" - NO MATCH
- Line 429: Check memory retrieval triggers - NO MATCH
- Line 514: Check "aid use the database" - NO MATCH

---

### 8. Normal Chat Flow
**File:** auto_response.py, Line 583-613
```python
else:  # Normal chat
    if not state["interactive_mode"]:  # True
        memory_context_text = ""
        rag_context_text = ""

        # No memory retrieval buffer
        content_to_send = content  # "Hey AiD"

        # Get call_aid_api function
        call_aid_api_local = call_aid_api  # Retrieved successfully
```

---

### 9. **CRITICAL POINT:** Call AID API via Executor
**File:** auto_response.py, Line 613
```python
reply = await loop.run_in_executor(executor, call_aid_api_local, content_to_send, rag_context_text, memory_context_text)
```
**Parameters:**
- content_to_send: "Hey AiD"
- rag_context_text: ""
- memory_context_text: ""

**This hands off execution to bot.py's call_aid_api function in a thread pool**

---

### 10. call_aid_api - Entry Point
**File:** bot.py, Line 415-425
```python
def call_aid_api(user_message, rag_context_text="", memory_context_text=""):
    global message_counter, conversation_state
    message_counter += 1  # Now 1
    start_time = time.time()

    print(f"\n{'='*60}")
    print(f"[CALL #{message_counter}] Processing: '{user_message[:50]}...'")
```
**Logs:**
- `============================================================` ✅ SEEN
- `[CALL #1] Processing: 'Hey AiD...'` ✅ SEEN

---

### 11. Memory Retrieval
**File:** bot.py, Line 446-508
```python
from memory_management import retrieve_memories, format_memories_for_context

print(f"[MEMORY RETRIEVAL] Retrieving relevant memories...")
retrieved_memories = retrieve_memories(user_message, top_k=15)
```
**Logs:**
- `[MEMORY RETRIEVAL] Retrieving relevant memories...` ✅ SEEN
- `[MEMORY STORE] Loading embedding model...` ✅ SEEN
- `[MEMORY RETRIEVAL] Found 5 high-quality memories` ✅ SEEN
- `[MEMORY 1] Score: 1.44 | ...` ✅ SEEN

---

### 12. Persona Systems (Emotion, Vulnerability, Conversation)
**File:** bot.py, Line 514-594
- Emotional analysis runs
- Vulnerability matching runs
- Conversation intelligence runs

**Logs:**
- `[EMOTION] Detected: neutral` ✅ SEEN
- `[VULNERABILITY] Level: low` ✅ SEEN
- `[CONVERSATION] Strategy: brief depth` ✅ SEEN

---

### 13. Build Context & Determine Mode
**File:** bot.py, Line 627-634
```python
context_data = memory.build_prompt(
    user_message=user_message,
    rag_context=rag_context_text,
    memory_context=memory_context_text
)

mode = context_data["mode"]  # "memory"
total_tokens = context_data["token_breakdown"]["total"]
```
**Logs:**
- `============================================================` ✅ SEEN
- `[MODE] MEMORY` ✅ SEEN
- `[TOKENS] Breakdown: ... TOTAL: 1770 / 28000` ✅ SEEN

---

### 14. Set max_tokens Based on Mode
**File:** bot.py, Line 738-754
```python
else:
    if mode == "chat":
        max_response_tokens = 400
    elif mode == "memory":
        max_response_tokens = 300  # THIS ONE
```
**Log:** `[MAX TOKENS] memory mode - limiting to 300 tokens` ✅ SEEN

---

### 15. API Request to Text-Gen-WebUI
**File:** bot.py, Line 774-822
```python
payload = {
    "model": MODEL_NAME,
    "prompt": context_data["prompt"],
    "max_new_tokens": max_response_tokens,
    ...
}

try:
    resp = requests.post(API_URL, json=payload, timeout=180)
    data = resp.json()
    raw_reply = data.get("content", "").strip()

    print(f"[DEBUG] Raw response length: {len(raw_reply)} chars")
    reply = clean_response(raw_reply, mode=mode)
    print(f"[DEBUG] Cleaned response ({mode} mode): {len(reply)} chars")
```
**Logs:**
- `[DEBUG] Raw response length: 76 chars` ✅ SEEN
- `[DEBUG] Cleaned response (memory mode): 76 chars` ✅ SEEN

**Reply content:** Unknown 76-character string

---

### 16. Background Post-Processing Thread
**File:** bot.py, Line 830-894
```python
def post_process_response():
    # Store in runtime, create memories, update relationship, etc.
    ...

print("[DEBUG] After response processing, launching background post-processing")
try:
    import threading
    post_process_thread = threading.Thread(target=post_process_response, daemon=True)
    post_process_thread.start()
except Exception as e:
    print(f"[WARN] Failed to start post-processing thread: {e}")
```
**Log:** `[DEBUG] After response processing, launching background post-processing` ✅ SEEN

---

### 17. **FAILURE ZONE** - Debug Logging
**File:** bot.py, Line 896-938
```python
end_time = time.time()

try:
    debug_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "message_number": message_counter,
        "mode": mode,
        "relationship_stage": relationship.get_current_stage() if PERSONA_SYSTEMS_LOADED else "unknown",
        "intimacy_score": round(relationship.get_intimacy_score(), 1) if PERSONA_SYSTEMS_LOADED else 0,
        ...
    }
    # Save to aid_logs.json
except Exception as e:
    print(f"[WARN] Failed to save debug log: {e}")
    traceback.print_exc()
```

**ISSUE:** If `relationship.get_current_stage()` or `relationship.get_intimacy_score()` throws an exception even with PERSONA_SYSTEMS_LOADED=True, this might fail silently.

---

### 18. Console Output
**File:** bot.py, Line 940-953
```python
print(f"[INFO] Response in {end_time - start_time:.2f}s | Mode: {mode.upper()}")
print(f"       [ORCHESTRATOR] Memories used: {len(orchestrator_memories)}")
```
**Logs:**
- `[INFO] Response in 2.78s | Mode: MEMORY` ✅ SEEN
- `[ORCHESTRATOR] Memories used: 0` ✅ SEEN

---

### 19. **CRITICAL MISSING LOGS**
**File:** bot.py, Line 944-956
```python
# Defensive logging - catch errors to prevent blocking response
try:
    print(f"       [MEMORY] Runtime: {memory.get_runtime_size()} | STM: {len(mem_stm.get_all())}")
except Exception as e:
    print(f"       [MEMORY] Error getting stats: {e}")

try:
    print(f"       [RELATIONSHIP] Stage: {relationship.get_current_stage()} | Intimacy: {relationship.get_intimacy_score():.0f}/100")
except Exception as e:
    print(f"       [RELATIONSHIP] Error getting stats: {e}")

print(f"[DEBUG] About to return reply: {len(reply)} chars")
return reply
```

**Expected Logs:** ❌ NOT SEEN
- `[MEMORY] Runtime: ... | STM: ...` OR `[MEMORY] Error getting stats: ...`
- `[RELATIONSHIP] Stage: ... | Intimacy: ...` OR `[RELATIONSHIP] Error getting stats: ...`
- `[DEBUG] About to return reply: 76 chars`

---

## 🚨 DIAGNOSIS

### The Function Never Returns

The logs stop at line 942 (`[ORCHESTRATOR] Memories used: 0`).

The next lines (944-956) are **NEVER EXECUTED**, which means:

1. **The bot.py process is CRASHING** between line 942 and line 944
2. **OR the thread is hanging/deadlocking** and never proceeds

### Most Likely Culprit

**Hypothesis:** The Python interpreter is crashing or the process is being killed between line 942 and 944.

This could be:
- Segmentation fault (C-level crash)
- Out of memory error
- Signal handler killing the process
- Infinite loop in memory.get_runtime_size() or mem_stm.get_all()

### Why We're Not Seeing Errors

Because `call_aid_api` runs in a `ThreadPoolExecutor`, if it crashes:
- The main thread doesn't see the exception
- No traceback is printed
- auto_response.py waits forever for a return value that never comes
- Discord never receives a message

---

## 🔍 ROOT CAUSE IDENTIFIED

### The Deadlock

The crash was caused by a **threading deadlock** in `_runtime_lock`:

1. `call_aid_api()` launches `post_process_response()` in background thread (line 891)
2. Background thread calls `memory.add_to_runtime()` which acquires `_runtime_lock`
3. Main thread (still in `call_aid_api`) tries to call `memory.get_runtime_size()` (line 975)
4. `memory.get_runtime_size()` tries to acquire `_runtime_lock`
5. **DEADLOCK** - Main thread waits forever for lock held by background thread
6. Function never returns, Discord never gets response

### The Fix (Commit: dcca47e)

**Capture stats BEFORE launching background thread:**
- Get `runtime_size_snapshot = memory.get_runtime_size()` BEFORE thread creation
- Get `stm_size_snapshot`, `current_stage_snapshot`, `intimacy_snapshot` as well
- Use snapshots for all subsequent logging
- **No lock contention = No deadlock**

### Testing

Restart bot and send "Hey AiD" - should now see:
```
[DEBUG_TRACE] Getting stats BEFORE background thread to avoid deadlock
[DEBUG_TRACE] Stats captured: runtime=199, stm=199, stage=mid, intimacy=55.2
[DEBUG] After response processing, launching background post-processing
[DEBUG_TRACE] End time captured: ...
...
[DEBUG] About to return reply: 32 chars
[DEBUG_TRACE] Returning reply to auto_response.py
```

Response should successfully reach Discord!
