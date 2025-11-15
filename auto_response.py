# auto_response.py
import asyncio
import traceback
import re
import os
import inspect
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# RAG pieces (same names as used in original on_message)
try:
    from rag_query import async_query
except Exception:
    async_query = None

try:
    from rag_loader import model_loaded_event
except Exception:
    model_loaded_event = None

# Memory modules used by the handler
try:
    from memory_management import stm as mem_stm
    from memory_management import emotion as mem_emotion
    from memory_management import categories as mem_categories
    from memory_management import summary as mem_summary
    from memory_management import phrasing as mem_phrasing
    from memory_management import utils as mem_utils
except Exception:
    # Lazy import fallback inside functions if memory_management package not available at import time
    mem_stm = mem_emotion = mem_categories = mem_summary = mem_phrasing = mem_utils = None

def format_date(ts):
    try:
        return datetime.fromisoformat(ts).strftime("%b %d, %Y")
    except Exception:
        return "Unknown"

# =========================
# STARTUP DEFENSIVE CHECKS
# =========================
def perform_startup_checks():
    warnings = []

    # Check memory_management modules
    modules_to_check = [
        ("memory_management.stm", "mem_stm"),
        ("memory_management.emotion", "mem_emotion"),
        ("memory_management.categories", "mem_categories"),
        ("memory_management.summary", "mem_summary"),
        ("memory_management.phrasing", "mem_phrasing"),
        ("memory_management.utils", "mem_utils"),
    ]

    for mod_name, var_name in modules_to_check:
        try:
            __import__(mod_name)
        except ImportError:
            warnings.append(f"âš ï¸ Module missing: {mod_name}")

    # Check required functions
    try:
        import memory_management.categories as mem_categories
        if not hasattr(mem_categories, "handle_memory_creation"):
            warnings.append("âš ï¸ Required function missing: handle_memory_creation in memory_management.categories")
    except Exception:
        pass

    try:
        import memory_management.summary as mem_summary
        if not hasattr(mem_summary, "summarize_with_correction"):
            warnings.append("âš ï¸ Required function missing: summarize_with_correction in memory_management.summary")
    except Exception:
        pass

    # Check optional RAG components
    try:
        import rag_loader
        if not hasattr(rag_loader, "model_loaded_event"):
            warnings.append("âš ï¸ model_loaded_event missing in rag_loader")
    except ImportError:
        warnings.append("âš ï¸ Module missing: rag_loader")

    try:
        import rag_query
        if not hasattr(rag_query, "async_query"):
            warnings.append("âš ï¸ async_query missing in rag_query")
    except ImportError:
        warnings.append("âš ï¸ Module missing: rag_query")

    # Check call_aid_api in bot.py (__main__)
    import sys, inspect
    bot_mod = sys.modules.get("__main__")
    if bot_mod and not hasattr(bot_mod, "call_aid_api"):
        warnings.append("âš ï¸ call_aid_api function not found in bot.py")

    # Output results
    if warnings:
        print("\n[Auto-Response Startup Warnings]\n" + "\n".join(warnings) + "\n")
    else:
        print("âœ… All auto-response dependencies found and ready.")
perform_startup_checks()


# Local defaults for globals
_default_executor = ThreadPoolExecutor(max_workers=2)

# Tries to extract helpers from the module that defined the `bot` object.
def _resolve_helpers(bot, call_aid_api_override=None):
    """
    Given a bot instance, find or create:
      - call_aid_api (callable)
      - executor (ThreadPoolExecutor-like)
    Returns a dict with keys 'call_aid_api' and 'executor'.
    """
    helpers = {}
    bot_mod = inspect.getmodule(bot)

    # call_aid_api: use the override if provided, otherwise look in bot module
    if call_aid_api_override is not None:
        call_aid_api = call_aid_api_override
    elif bot_mod:
        call_aid_api = getattr(bot_mod, "call_aid_api", None)
    else:
        call_aid_api = None
    helpers["call_aid_api"] = call_aid_api

    # executor (try to reuse an executor if provided by bot module)
    executor = None
    if bot_mod:
        executor = getattr(bot_mod, "executor", None)
    if executor is None:
        executor = _default_executor
    helpers["executor"] = executor

    # Provide model_loaded_event if available in bot module (fallback to imported)
    if bot_mod and hasattr(bot_mod, "model_loaded_event"):
        helpers["model_loaded_event"] = getattr(bot_mod, "model_loaded_event")
    else:
        helpers["model_loaded_event"] = model_loaded_event

    # Provide async_query if available in bot module (fallback to imported)
    if bot_mod and hasattr(bot_mod, "async_query"):
        helpers["async_query"] = getattr(bot_mod, "async_query")
    else:
        helpers["async_query"] = async_query

    return helpers


def register_handlers(bot, call_aid_api_override=None):
    """
    Register the full automatic-response on_message handler to the provided bot.
    This restores the original behavior: interactive memory creation/retrieval,
    RAG queries, and normal chat flow.
    """
    # resolve call_aid_api + executor from the bot's defining module (if present)
    helpers = _resolve_helpers(bot, call_aid_api_override=call_aid_api_override)
    call_aid_api = helpers["call_aid_api"]
    executor = helpers["executor"]
    resolved_model_loaded_event = helpers.get("model_loaded_event")
    resolved_async_query = helpers.get("async_query")

    # Ensure memory modules are available (in case they weren't at import)
    global mem_stm, mem_emotion, mem_categories, mem_summary, mem_phrasing, mem_utils
    if mem_stm is None:
        try:
            from memory_management import stm as mem_stm
            from memory_management import emotion as mem_emotion
            from memory_management import categories as mem_categories
            from memory_management import summary as mem_summary
            from memory_management import phrasing as mem_phrasing
            from memory_management import utils as mem_utils
        except Exception:
            # If still failing, we will raise at runtime when those features are used
            pass

    # Module-level state used by the handler (keeps parity with original)
    state = {
        "interactive_mode": False,
        "pending_memory_context": None,
        "memory_retrieval_buffer": None,
        "memory_context_for_model": None
    }

    MEMORY_RETRIEVE_TRIGGERS = [
        "aid do you remember",
        "aid jog your memory on",
        "aid check your notes on",
        "aid recall anything about"
    ]

    # The actual on_message handler (faithful to the original logic)
    async def _on_message(message):
        print(f"[AUTO_RESPONSE] on_message triggered for message: {message.content[:50]}")
        # Access & modify outer state
        nonlocal state

        # Try to mirror original guard: ignore messages from the bot itself
        if message.author == bot.user:
            return

        # === NEW: Let commands pass through without AI response ===
        if message.content.strip().startswith("!"):
            try:
                await bot.process_commands(message)
            except Exception as e:
                print(f"[ERROR] Command processing failed: {e}")
            return  # Don't process as conversation

        # === IMPORTS NEEDED IN THIS HANDLER ===
        try:
            from memory_management import retrieval as mem_retrieval
        except Exception:
            mem_retrieval = None
    
        try:
            from memory_management import persistent as mem_persist
        except Exception:
            mem_persist = None

        try:
            # allow commands to be processed as before
            try:
                await bot.process_commands(message)
            except Exception:
                print("[WARN] bot.process_commands raised:")
                traceback.print_exc()
        except Exception:
            # If processing commands raised fatal error, continue to on_message logic
            traceback.print_exc()

        content = message.content.strip()
        loop = asyncio.get_event_loop()
        reply = None  # Ensure defined

        try:
            # --- Toggle back to chat mode ---
            if content.lower() == "back to the chat":
                state["interactive_mode"] = False
                if state["memory_retrieval_buffer"]:
                    # CRITICAL: Store memory for next API call as RAG context
                    # Don't send it to Discord (too long), don't add it to runtime
                    print(f"[INFO] Memory ({len(state['memory_retrieval_buffer'])} chars) will be used as RAG context")
                    
                    # Keep the memory in the buffer for the next message
                    # It will be passed to call_aid_api as rag_context_text
                    # (Don't clear it here, clear it after use)
                    pass  # Memory stays in buffer

                try:
                    await message.channel.send(mem_phrasing.get_random_back_to_chat())
                except Exception as e:
                    print(f"[WARN] Failed to send back-to-chat confirmation: {e}")

                state["pending_memory_context"] = None
                return

            print(f"[DEBUG] Interactive mode: {state['interactive_mode']}")
            print(f"[DEBUG] Pending memory context type: {type(state['pending_memory_context'])}")
            print(f"[DEBUG] Content: '{content}' | isdigit: {content.isdigit()}")

            # --- Block normal messages in interactive mode ---
            if state["interactive_mode"] and not content.lower().startswith("aid create a memory") and not content.lower().startswith("aid use the database"):
                # allow numeric selection when pending_memory_context is list
                if state["memory_retrieval_buffer"] is None and state["pending_memory_context"] and isinstance(state["pending_memory_context"], list) and content.isdigit():
                    idx = int(content) - 1
    
                    if 0 <= idx < len(state["pending_memory_context"]):
                        mem = state["pending_memory_context"][idx]
        
                        print(f"[DEBUG] Memory ID being retrieved: {mem.get('id', 'None')}")
        
                        # === STEP 1: Retrieve full content ===
                        try:
                            from memory_management import retrieval as mem_retrieval
                            memory_content = mem_retrieval.retrieve_full_entry(mem.get('id', ''))
            
                            # Fallback if retrieval returned empty
                            if not memory_content:
                                print(f"[WARN] retrieve_full_entry returned empty, trying direct JSON lookup")
                                import json, os
                                memory_file = "memory_management/backups/long_term_memory.json"
                                if os.path.exists(memory_file):
                                    with open(memory_file, "r", encoding="utf-8") as f:
                                        all_memories = json.load(f)
                                    for m in all_memories:
                                        if m.get("id") == mem.get("id"):
                                            memory_content = m.get("content", "")
                                            print(f"[FALLBACK] Found memory in JSON: {len(memory_content)} chars")
                                            break
            
                            if not memory_content:
                                print(f"[ERROR] Could not retrieve memory content for {mem.get('id')}")
                                memory_content = "Memory content unavailable."
                            else:
                                print(f"[DEBUG] Retrieved memory: {len(memory_content)} chars (~{len(memory_content.split())} words)")
            
                        except Exception as e:
                            print(f"[ERROR] Failed to retrieve full memory: {e}")
                            import traceback
                            traceback.print_exc()
                            memory_content = f"Error retrieving memory: {e}"
        
                        # === STEP 2: Store in buffer ===
                        state["memory_retrieval_buffer"] = memory_content
        
                        # === STEP 3: Activate in persistent pool ===
                        try:
                            from memory_management import persistent as mem_persist
            
                            # Build complete memory object with FULL content
                            full_mem = {
                                "id": mem.get("id"),
                                "title": mem.get("title", "Untitled"),
                                "content": memory_content,  # Full content from retrieval
                                "summary": mem.get("summary", ""),
                                "corrected_summary": mem.get("corrected_summary", ""),
                                "tags": mem.get("tags", []),
                                "category_path": mem.get("category_path", [])
                            }
            
                            mem_persist.activate_memory(full_mem, initial_strength=1.0, priority="manual")
                            print(f"[MANUAL] Activated {mem.get('id')} in persistent pool (priority: manual)")
            
                        except Exception as e:
                            print(f"[WARN] Failed to activate in persistent pool: {e}")
                            import traceback
                            traceback.print_exc()
        
                        # === STEP 4: Send confirmation ===
                        confirmation_text = f"ðŸ“‚ Memory ID {idx+1} selected. Full content will be pasted into the chat when you type 'Back to the chat'."
                        try:
                            await message.channel.send(confirmation_text)
                        except Exception as e:
                            print(f"[WARN] Failed to send memory selection confirmation: {e}")
        
                        # === STEP 5: Memory retrieval confirmation ===
                        if mem and state["memory_retrieval_buffer"]:
                            try:
                                mem_id = mem.get("id", "Unknown ID")
                                print(f"[INFO] Memory {mem_id} successfully retrieved and loaded into buffer.")
                                await message.channel.send(f"ðŸ§  I've now fully recalled memory ID {idx+1}.")
                            except Exception as e:
                                print(f"[WARN] Memory retrieval confirmation failed: {e}")
        
                        state["pending_memory_context"] = None
                    else:
                        try:
                            await message.channel.send("âŒ Invalid ID number. Pick a valid memory ID from the list.")
                        except Exception as e:
                            print(f"[WARN] Failed to send invalid ID message: {e}")
    
                    return
                # In interactive mode, ignore other normal messages (preserve mode)
                return

            print(f"[AUTO_RESPONSE] Checking message triggers for: {content[:50]}")
            # --- Memory creation trigger ---
            if content.lower().startswith("aid create a memory"):
                state["interactive_mode"] = True

                # import inside handler to reflect latest module state
                try:
                    import memory_management.categories as mm_categories
                    import memory_management.utils as mm_utils
                    import memory_management.summary as mm_summary
                except Exception as e:
                    print(f"[ERROR] Failed to import memory_management modules: {e}")
                    traceback.print_exc()
                    await message.channel.send("âŒ Memory system currently unavailable.")
                    return

                # Hands control to the categories handler to create a memory (async)
                memory_entry = None
                try:
                    memory_entry = await mm_categories.handle_memory_creation(bot, message)
                except Exception as e:
                    print(f"[ERROR] handle_memory_creation failed: {e}")
                    traceback.print_exc()
                    await message.channel.send("âŒ Memory creation failed during interaction.")
                    return

                if not memory_entry:
                    try:
                        await message.channel.send("âŒ Memory creation skipped or timed out.")
                    except Exception:
                        pass
                    return

                # Summarize content if present
                if memory_entry.get("content"):
                    try:
                        summary_data = mm_summary.summarize_with_correction(memory_entry["content"])
                        memory_entry["summary"] = summary_data.get("ai_summary", "")
                    except Exception as e:
                        print(f"[WARN] Summarization failed: {e}")
                        memory_entry["summary"] = ""
                else:
                    memory_entry["summary"] = ""

                memory_file = "memory_management/backups/long_term_memory.json"
                try:
                    os.makedirs(os.path.dirname(memory_file), exist_ok=True)
                except Exception:
                    pass

                try:
                    memories = mm_utils.load_json(memory_file, default=[])
                except Exception:
                    memories = []

                memories.append(memory_entry)
                try:
                    mm_utils.save_json(memory_file, memories)
                except Exception as e:
                    print(f"[WARN] failed to save long_term_memory.json: {e}")

                state["pending_memory_context"] = memory_entry

                try:
                    await message.channel.send(f"âœ… Memory saved under category: {'/'.join(memory_entry.get('category_path', ['Uncategorized']))}")
                except Exception:
                    pass

                reply = f"Memory saved under category: {'/'.join(memory_entry.get('category_path', ['Uncategorized']))}' with summary generated."

            # --- Memory retrieval trigger ---
            elif any(content.lower().startswith(trigger) for trigger in MEMORY_RETRIEVE_TRIGGERS):
                try:
                    import memory_management.utils as mm_utils
                except Exception:
                    await message.channel.send("âŒ Memory utilities unavailable.")
                    return

                memory_file = "memory_management/backups/long_term_memory.json"
                memories = mm_utils.load_json(memory_file, default=[])
                
                # Show playful searching phrase
                try:
                    await message.channel.send(mem_phrasing.get_random_search_phrase())
                except Exception:
                    pass

                trigger = next(t for t in MEMORY_RETRIEVE_TRIGGERS if content.lower().startswith(t))
                query_text = content[len(trigger):].strip()
                if not query_text:
                    await message.channel.send("âš ï¸ Please provide something to search for in your memories.")
                    return

                # --- Word-based, case-insensitive scoring ---
                query_words = set(re.findall(r"\w+", query_text.lower()))
                scored_memories = []

                for mem in memories:
                    fields_to_check = []
                    if mem.get("title"):
                        fields_to_check.append(mem["title"])
                    if mem.get("summary"):
                        fields_to_check.append(mem["summary"])
                    if mem.get("tags"):
                        fields_to_check.append(" ".join(mem["tags"]))
                    if mem.get("category_path"):
                        fields_to_check.append(" ".join(mem["category_path"]))

                    words_in_mem = set()
                    for field in fields_to_check:
                        words_in_mem.update(re.findall(r"\w+", str(field).lower()))

                    match_count = len(query_words & words_in_mem)
                    if match_count > 0:
                        scored_memories.append((match_count, mem))

                if not scored_memories:
                    await message.channel.send(mem_phrasing.get_random_not_found())
                    return

                scored_memories.sort(key=lambda x: x[0], reverse=True)
                matching_memories = [m for _, m in scored_memories]

                # --- FIXED: Send memories individually to avoid 2000 char limit ---
                try:
                    await message.channel.send("ðŸ”Ž Found these memories (sorted by relevance):")
                    
                    for idx, m in enumerate(matching_memories):
                        date_str = format_date(m.get('timestamp'))
                        category_str = '/'.join(m.get('category_path', ['Uncategorized']))
                        full_summary = m.get('summary') or m.get('content') or "No summary available."
                        
                        # Build individual memory message
                        mem_msg = f"ID: {idx+1} | Category: {category_str} | Date: {date_str}\nAI Summary:\n{full_summary}"
                        
                        # If single memory exceeds limit, chunk it
                        if len(mem_msg) > 1900:
                            chunks = [mem_msg[i:i+1900] for i in range(0, len(mem_msg), 1900)]
                            for chunk in chunks:
                                await message.channel.send(chunk)
                        else:
                            await message.channel.send(mem_msg)
                    
                    await message.channel.send(
                        "Type the ID number to select a memory. The full content will be pasted into the chat when you type 'Back to the chat'."
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to send memory list: {e}")
                    traceback.print_exc()

                # CRITICAL: Set state AFTER sending (or attempting to send)
                state["pending_memory_context"] = matching_memories
                state["interactive_mode"] = True
                return

            # --- Database / RAG query ---
            elif content.lower().startswith("aid use the database"):
                query_text = content[len("aid use the database"):].strip()
                if not query_text:
                    await message.channel.send("âš ï¸ Please provide a query after the trigger phrase.")
                    return

                # Use phrasing helper if available
                try:
                    from memory_management.phrasing import get_random_rag_phrase
                    random_phrase = get_random_rag_phrase()
                except Exception:
                    random_phrase = "Searching the database..."

                try:
                    await message.channel.send(f"ðŸ” {random_phrase}")
                except Exception:
                    pass

                print(f"[RAG] Received query: {query_text}")

                # Wait for model_loaded_event if available
                if resolved_model_loaded_event is not None:
                    try:
                        await resolved_model_loaded_event.wait()
                    except Exception:
                        pass

                if resolved_async_query is None:
                    await message.channel.send("âŒ RAG query subsystem is unavailable.")
                    return

                try:
                    rag_results = await resolved_async_query(query_text, top_k=5)
                except Exception as e:
                    print(f"[ERROR] async_query failed: {e}")
                    traceback.print_exc()
                    await message.channel.send("âŒ RAG query failed.")
                    return

                rag_texts = []
                for r in rag_results:
                    try:
                        if isinstance(r, dict):
                            txt = r.get("text") or r.get("content") or r.get("paragraph") or ""
                        else:
                            txt = str(r)
                    except Exception:
                        txt = str(r)
                    rag_texts.append(txt)

                rag_context_text = "\n".join(rag_texts)
                full_user_message = f"User question: {query_text}"

                # call_aid_api may be absent in some bot.py variants; attempt to find it on the bot module otherwise error
                if call_aid_api is None:
                    # try to find call_aid_api on the module that defined `bot`
                    bot_mod = inspect.getmodule(bot)
                    call_aid_api_local = getattr(bot_mod, "call_aid_api", None) if bot_mod else None
                else:
                    call_aid_api_local = call_aid_api

                if not call_aid_api_local:
                    await message.channel.send("âŒ AID API call function unavailable.")
                    return

                # run the blocking call in executor (to mirror original behavior)
                reply = await loop.run_in_executor(executor, call_aid_api_local, full_user_message, rag_context_text)

            # --- Normal chat ---
            else:
                if not state["interactive_mode"]:
                    # Check if we have a retrieved memory to use as MEMORY context
                    memory_context_text = ""
                    rag_context_text = ""
        
                    if state.get("memory_retrieval_buffer"):
                        # Pass memory as MEMORY context (3rd parameter)
                        memory_context_text = state["memory_retrieval_buffer"]
                        print(f"[INFO] Using retrieved memory as memory context ({len(memory_context_text)} chars)")
                        state["memory_retrieval_buffer"] = None  # Clear after use
        
                    content_to_send = content

                    # find call_aid_api (again, allow fallback to bot module)
                    if call_aid_api is None:
                        bot_mod = inspect.getmodule(bot)
                        call_aid_api_local = getattr(bot_mod, "call_aid_api", None) if bot_mod else None
                    else:
                        call_aid_api_local = call_aid_api

                    if not call_aid_api_local:
                        # If function missing, inform user
                        try:
                            await message.channel.send("Ã¢Å’ AID engine unavailable. contact admin.")
                        except Exception:
                            pass
                        return

                    # Pass memory in correct parameter position (3rd)
                    reply = await loop.run_in_executor(executor, call_aid_api_local, content_to_send, rag_context_text, memory_context_text)
                    print(f"[AUTO_RESPONSE] Received reply from call_aid_api: {len(reply) if reply else 0} chars")
            print(f"[AUTO_RESPONSE] REACHED SEND SECTION - reply variable: {type(reply)} {len(str(reply)) if reply else 0} chars")

            # --- Send reply strictly in 2000-char chunks ---
            reply_text = reply if isinstance(reply, str) else str(reply)
            print(f"[AUTO_RESPONSE] Converted reply to text: {len(reply_text)} chars")
            
            if not reply_text.strip():
                reply_text = "⚠️ AID generated a response, but it was empty. Check logs."
            
            print(f"[AUTO_RESPONSE] About to send reply to Discord: {len(reply_text)} chars")

            max_len = 2000
            for i in range(0, len(reply_text), max_len):
                chunk = reply_text[i:i + max_len]
                print(f"[AUTO_RESPONSE] Attempting to send chunk {i//2000 + 1}: {len(chunk)} chars")
                try:
                    await message.channel.send(chunk)
                    print(f"[AUTO_RESPONSE] Successfully sent chunk to Discord")
                except Exception as send_e:
                    print(f"[ERROR] Failed to send message chunk to Discord: {send_e}")
                    traceback.print_exc()

            print(f"[AUTO_RESPONSE] Completed message handler successfully")
        except Exception as e:
            print(f"[ERROR] on_message handling failed: {e}")
            traceback.print_exc()

    # Register the handler on the bot
    # Use add_listener to avoid decorator-time binding issues
    bot.add_listener(_on_message, "on_message")

    # Return the state object in case caller wants to inspect/modify it
    return state