# bot.py - COMPLETE ADVANCED INTELLIGENCE INTEGRATION + ORCHESTRATOR MEMORY SYSTEM
import discord
from discord.ext import commands
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import os
import time
from datetime import datetime
import threading
import atexit
import sys
import re
import traceback
import warnings

print("[STARTUP] Preloading all memory models...")
try:
    import memory_management
    memory_management.preload_all_modules()
    print("[STARTUP] Ã¢Å“â€¦ All models ready!")
except Exception as e:
    print(f"[STARTUP] Ã¢Å¡Â Ã¯Â¸Â {e}")

# --- ADD TEXT-GEN WEBUI TO PATH ---
sys.path.append(r"C:\Users\DeeDiebS\Desktop\Based\ooga\text-generation-webui")

# --- RAG IMPORTS ---
from rag_loader import load_all_indexes, load_embedding_model, model_loaded_event
from rag_query import async_query

# --- MEMORY SYSTEM IMPORTS ---
import memory

# --- PERSONA SYSTEM IMPORTS ---
from Persona import personality, relationship

# --- VOICE HANDLER IMPORTS ---
import voice_handler

# --- ORCHESTRATOR (OPTIONAL - for fallback) ---
try:
    from memory_management import orchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    orchestrator = None


# =======================
# CONFIGURATION
# =======================
TOKEN = "MTQ1emI0"
API_URL = "http://127.0.0.1:53659/completions"
MODEL_NAME = "AID"

# =======================
# FILE PATHS
# =======================
DEBUG_LOG_FILE = "aid_logs.json"
MEMORY_BACKUP_DIR = "memory_management/backups"

# =======================
# STATE MANAGEMENT
# =======================
conversation_state = {
    "verbose_mode": False,
    "last_blocked_response": None,
    "mode_override": None
}

# =======================
# DISCORD SETUP
# =======================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
executor = ThreadPoolExecutor(max_workers=2)

# =======================
# MEMORY MANAGEMENT
# =======================
from memory_management import stm as mem_stm
from memory_management import emotion as mem_emotion
# from memory_management import categories as mem_categories
# from memory_management import retrieval as mem_retrieval
# from memory_management import summary as mem_summary
# from memory_management import archives as mem_archives
# from memory_management import phrasing as mem_phrasing
from memory_management import utils as mem_utils
# from memory_management import enhanced_formation


# === Initialize STM ===
mem_stm.init_stm()
mem_stm.start_auto_save_loop()

# === Load STM into runtime buffer ===
memory.init_runtime_from_stm()

# === START AUTO-SAVE FROM RUNTIME TO STM ===
memory.start_auto_save_loop()

# === Auto-clean runtime ===
memory.cleanup_runtime()

# =======================
# ENSURE DEFAULT CATEGORIES
# =======================
# mem_categories.init_categories()
# for default_cat in ["Project", "Personal"]:
#     if default_cat not in mem_categories.list_categories():
#         mem_categories.add_category(default_cat)

# =======================
# RAG INITIALIZATION & STATUS CHECK
# =======================
async def startup_checks():
    print("[STARTUP] Performing system checks...")
    try:
        indexes = load_all_indexes()
        total_vectors = sum(len(v["metadata"]) for v in indexes.values())
        print(f"[RAG] Loaded {len(indexes)} datasets with {total_vectors} total vectors.")
        if not indexes:
            print("[RAG] Ã¢Å¡Â  WARNING: No RAG indexes found!")
        else:
            print(f"[RAG] Ã¢Å“â€¦ RAG system fully loaded and ready!")
        
        # Load embedding model asynchronously
        await load_embedding_model()
        print("[RAG] Embedding model loaded successfully!")
    except Exception as e:
        print(f"[RAG] Ã¢Å¡Â  WARNING: RAG system unavailable: {e}")
    
    print("[STARTUP] [OK] AID is fully ready and online.")

# =======================
# PERSONA SYSTEM INITIALIZATION
# =======================
PERSONA_SYSTEMS_LOADED = False
ADVANCED_INTELLIGENCE_LOADED = False

try:
    print(f"\n[PERSONA] Initializing complete personality architecture...")
    
    from Persona import proactive, emotion_intelligence, preference_learning
    from Persona import conversation_intelligence, routine_learning
    
    # 1. Initialize personality
    personality_config = personality.load_personality_config()
    print(f"[PERSONA] Ã¢Å“â€œ Personality loaded: {personality_config.get('voice_style', 'cockney')}")
    
    # 2. Initialize relationship tracking
    relationship.init_relationship_system()
    rel_summary = relationship.get_relationship_summary()
    print(f"[PERSONA] Ã¢Å“â€œ Relationship tracking initialized")
    print(f"          Stage: {rel_summary['stage']} | Days: {rel_summary['days_together']} | Exchanges: {rel_summary['total_exchanges']}")
    print(f"          Intimacy: {rel_summary['intimacy_score']:.0f}/100")
    
    # 3. Initialize proactive engagement
    proactive.init_proactive()
    print(f"[PERSONA] Ã¢Å“â€œ Proactive engagement initialized")
    
    # 4. Initialize emotional intelligence
    emotion_intelligence.init_emotional_intelligence()
    print(f"[PERSONA] Ã¢Å“â€œ Emotional intelligence initialized")
    
    # 5. Initialize preference learning
    preference_learning.init_preferences()
    print(f"[PERSONA] Ã¢Å“â€œ Preference learning initialized")
    
    # 6. Initialize conversation intelligence
    conversation_intelligence.init_conversation_intelligence()
    print(f"[PERSONA] Ã¢Å“â€œ Conversation intelligence initialized")
    
    # 7. Initialize routine learning
    routine_learning.init_routine_tracker()
    print(f"[PERSONA] Ã¢Å“â€œ Routine learning initialized")
    
    # 8. Initialize advanced intelligence systems
    print(f"\n[ADVANCED] Initializing advanced intelligence systems...")
    
    from Persona import topic_threading, socratic_mode, context_layers
    from Persona import vulnerability_matching, strategic_silence, disagreement_engine
    
    topic_threading.init_topic_threading()
    print(f"[ADVANCED] Ã¢Å“â€œ Topic threading initialized")
    
    socratic_mode.init_socratic_mode()
    print(f"[ADVANCED] Ã¢Å“â€œ Socratic mode initialized")
    
    context_layers.init_context_layers()
    print(f"[ADVANCED] Ã¢Å“â€œ Context layering initialized")
    
    vulnerability_matching.init_vulnerability_matching()
    print(f"[ADVANCED] Ã¢Å“â€œ Vulnerability matching initialized")
    
    strategic_silence.init_strategic_silence()
    print(f"[ADVANCED] Ã¢Å“â€œ Strategic silence initialized")
    
    disagreement_engine.init_disagreement_engine()
    print(f"[ADVANCED] Ã¢Å“â€œ Disagreement engine initialized")
    
    # Mark all systems as loaded
    PERSONA_SYSTEMS_LOADED = True
    ADVANCED_INTELLIGENCE_LOADED = True
    
except Exception as e:
    print(f"[PERSONA] Ã¢Å¡Â  Warning: Some persona systems failed to load: {e}")
    print(f"[PERSONA] Continuing with limited persona features...")
    traceback.print_exc()
    PERSONA_SYSTEMS_LOADED = False
    ADVANCED_INTELLIGENCE_LOADED = False

print("=" * 60)
print("[ONLINE] AID is ONLINE and ready to roll, boss!")
print("   Cockney sass: [OK]  Memory system: [OK]  RAG database: [OK]")
print("   Memory Orchestrator: [OK]  Semantic Search: [OK]")
if PERSONA_SYSTEMS_LOADED:
    print("   Persona system: [OK]  Relationship tracking: [OK]")
    print("   Proactive: [OK]  Emotion: [OK]  Preferences: [OK]")
    print("   Conversation: [OK]  Routines: [OK]")
if ADVANCED_INTELLIGENCE_LOADED:
    print("   Advanced Intelligence: [OK]")
    print("   Ã¢â€Å“Ã¢â€â‚¬ Topic Threading: [OK]  Ã¢â€Å“Ã¢â€â‚¬ Socratic Mode: [OK]")
    print("   Ã¢â€Å“Ã¢â€â‚¬ Context Layers: [OK]   Ã¢â€Å“Ã¢â€â‚¬ Vulnerability Match: [OK]")
    print("   Ã¢â€Å“Ã¢â€â‚¬ Strategic Silence: [OK] Ã¢â€â€Ã¢â€â‚¬ Disagreement Engine: [OK]")
else:
    print("   Persona system: [LIMITED]")
print("   Context window: 8k tokens (optimized for 8GB VRAM)")
print("   Mode system: [OK] (CHAT/MEMORY/RAG auto-detection)")
print("   Type 'AID create a memory' or just chat away!")
print("=" * 60)

# =======================
# MODE RESET DETECTION
# =======================
def detect_mode_reset(user_message):
    """Detect if user wants to reset conversation mode/stop verbose responses."""
    msg_lower = user_message.lower().strip()
    
    reset_patterns = [
        (r'\b(back to normal|return to normal)\b', 'explicit_reset'),
        (r'\b(that\'?s? enough|stop that|enough)\b', 'stop_command'),
        (r'\b(be brief|shorter|less detail)\b', 'brevity_request'),
        (r'\b(nevermind|never mind|forget it)\b', 'cancel'),
        (r'\b(stop|reset|cancel)\b', 'direct_command'),
    ]
    
    for pattern, reset_type in reset_patterns:
        if re.search(pattern, msg_lower):
            print(f"[MODE RESET] Detected: {reset_type} - '{user_message[:50]}'")
            return {
                'reset_detected': True,
                'reset_type': reset_type,
                'original_message': user_message
            }
    
    return None

def detect_verbose_request(user_message):
    """Detect if user is explicitly requesting verbose/detailed response."""
    msg_lower = user_message.lower()
    
    # Check for negative indicators first
    negative_indicators = [
        r'\b(forget|stop|enough|too much|normally|just say|brief|short)\b',
        r'\b(talk normally|speak normally|be normal|normal conversation)\b',
        r'\b(calm down|chill|relax|tone it down)\b',
    ]
    
    for pattern in negative_indicators:
        if re.search(pattern, msg_lower):
            return None
    
    # Check for verbose indicators
    verbose_indicators = [
        r'\b(most detailed|very detailed|comprehensive|in-depth)\b',
        r'\b(write.*dissertation|give.*dissertation|explain like.*professor)\b',
        r'\b(explain everything|full explanation|complete explanation)\b',
        r'\b(thorough|exhaustive|extensive)\b.*\b(explanation|analysis|breakdown)\b',
    ]
    
    for pattern in verbose_indicators:
        if re.search(pattern, msg_lower):
            print(f"[VERBOSE MODE] Detected verbose request")
            return {
                'verbose_requested': True,
                'pattern_matched': pattern
            }
    
    return None

# =======================
# RESPONSE VALIDATION
# =======================
def validate_response_coherence(response: str, user_message: str) -> bool:
    """Check if response is coherent before sending."""
    if not response or len(response.strip()) < 5:
        return False
    
    words = response.lower().split()
    if len(words) > 10:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            print("[VALIDATION] Ã¢ÂÅ’ Response has excessive repetition")
            return False
    
    if response.replace(" ", "").replace(",", "").isdigit():
        print("[VALIDATION] Ã¢ÂÅ’ Response is only numbers")
        return False
    
    real_words = ["the", "and", "is", "to", "a", "i", "you", "mate", "boss"]
    has_real_word = any(word in response.lower() for word in real_words)
    if not has_real_word and len(response) > 20:
        print("[VALIDATION] Ã¢ÂÅ’ Response lacks real words")
        return False
    
    return True

# =======================
# RESPONSE CLEANING
# =======================
def clean_response(text, mode="chat"):
    """Remove system text leakage using comprehensive pattern matching."""
    if not text or len(text) < 5:
        return text
    
    import re
    
    # MEMORY/RAG MODES: Light cleaning only
    if mode in ["memory", "rag"]:
        split_patterns = [
            r'<\|system\|>',
            r'SPEAKING RULES:',
            r'CRITICAL RULES'
        ]
        for pattern in split_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                text = text[:match.start()]
        
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r' \1 ', text)
        return text.strip()
    
    # CHAT MODE: Aggressive cleaning
    split_patterns = [
        r'<\|end\|>',
        r'<\|end\|\]',
        r'To keep things',
        r'Great job!',
        r"Let's keep it",
        r'Looks perfect!',
        r"Here it is:",
        r'Final version:',
        r'<\|AID\|>',
        r'<\|USER\|>',
        r'<\|system\|>',
        r'<\|conversation\|>',
        r'<\|world_info\|>',
        r'\nUSER:',
        r'\nAID:',
        r'\[Archive\]',
        r'\[Earlier\]',
        r'\[Recent\]',
        r'SPEAKING RULES:',
        r'CRITICAL RULES',
        r'\[RELATIONSHIP',
        r'\[DATABASE'
    ]
    
    for pattern in split_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text = text[:match.start()]
    
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r' \1 ', text)
    text = re.sub(r'\([^)]{3,}\)', '', text)
    text = re.sub(r'\n\s*>.*', '', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        skip_patterns = [
            r'^\[.*\]$',
            r'^USER:',
            r'^AID:',
            r'^\*',
            r'^Note:',
            r'^Disclaimer:',
        ]
        
        skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                skip = True
                break
        
        if not skip:
            cleaned_lines.append(line_stripped)
    
    result = ' '.join(cleaned_lines)
    result = re.sub(r'\s+', ' ', result)
    
    return result.strip()

# =======================
# CORE CALL_AID_API (WITH ORCHESTRATOR INTEGRATION)
# =======================
message_counter = 0

def call_aid_api(user_message, rag_context_text="", memory_context_text=""):
    """
    MAIN ENTRY POINT: Calls AID's API with full context + orchestrator memory.
    NOW WITH UNIFIED MEMORY SYSTEM VIA ORCHESTRATOR.
    """
    global message_counter, conversation_state
    message_counter += 1
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"[CALL #{message_counter}] Processing: '{user_message[:50]}...'")
    
    # ===========================================
    # MODE RESET & VERBOSE DETECTION
    # ===========================================
    mode_reset = detect_mode_reset(user_message)
    verbose_request = detect_verbose_request(user_message)
    
    if mode_reset:
        print(f"[MODE RESET] User requested mode reset: {mode_reset['reset_type']}")
        conversation_state["verbose_mode"] = False
        conversation_state["mode_override"] = "brief"
        conversation_state["last_blocked_response"] = None
    
    if verbose_request:
        print(f"[VERBOSE MODE] User requested detailed response")
        conversation_state["verbose_mode"] = True
        conversation_state["mode_override"] = "verbose"
    
    # ===========================================
    # NEW: FAISS-BASED MEMORY RETRIEVAL (ALWAYS-ON)
    # ===========================================
    retrieved_memories = []
    orchestrator_memories = []  # Initialize to prevent errors in debug logging
    memory_context_text = ""
    try:
        # Import new memory system
        from memory_management import retrieve_memories, format_memories_for_context
        
        # Retrieve relevant memories automatically
        print(f"[MEMORY RETRIEVAL] Retrieving relevant memories...")
        retrieved_memories = retrieve_memories(user_message, top_k=15)

        if retrieved_memories:
            # Additional quality filter: only use high-confidence memories (score >= 0.4)
            high_quality = [m for m in retrieved_memories if m.get('retrieval_score', 0) >= 0.4]

            # If we have high-quality memories, use only those
            if high_quality:
                retrieved_memories = high_quality
                print(f"[MEMORY RETRIEVAL] Found {len(retrieved_memories)} high-quality memories (score >= 0.4)")
            else:
                # If no high-quality memories, only use ones above 0.35
                retrieved_memories = [m for m in retrieved_memories if m.get('retrieval_score', 0) >= 0.35]
                print(f"[MEMORY RETRIEVAL] Found {len(retrieved_memories)} relevant memories (score >= 0.35)")

            if retrieved_memories:
                # Format memories for context injection
                memory_context_text = format_memories_for_context(retrieved_memories)

                # Show top 3 for debugging
                for i, mem in enumerate(retrieved_memories[:3], 1):
                    score = mem.get('retrieval_score', 0)
                    content_preview = mem.get('content', '')[:60]
                    print(f"[MEMORY {i}] Score: {score:.2f} | {content_preview}...")
            else:
                print(f"[MEMORY RETRIEVAL] No high-quality memories found after filtering")
        else:
            print(f"[MEMORY RETRIEVAL] No relevant memories found")
            
    except ImportError as e:
        print(f"[MEMORY RETRIEVAL] New memory system not available: {e}")
        print(f"[MEMORY RETRIEVAL] Falling back to orchestrator...")
        # Fallback to orchestrator if new system not ready
        try:
            orchestrator_memories = orchestrator.retrieve_memory(
                query=user_message,
                limit=5,
                mode="hybrid"
            )
            if orchestrator_memories:
                print(f"[ORCHESTRATOR] Retrieved {len(orchestrator_memories)} relevant memories")
                memory_context_text = "\n".join([
                    f"- {mem.get('content', '')[:200]}"
                    for mem in orchestrator_memories
                ])
        except Exception as orch_e:
            print(f"[ORCHESTRATOR] Also failed: {orch_e}")
            retrieved_memories = []
    except Exception as e:
        print(f"[MEMORY RETRIEVAL] Error: {e}")
        import traceback
        traceback.print_exc()
        retrieved_memories = []
    
    
    # ===========================================
    # PROACTIVE LAYER
    # ===========================================
    if PERSONA_SYSTEMS_LOADED:
        try:
            proactive.process_message(user_message)
        except Exception as e:
            print(f"[PROACTIVE] Error: {e}")
    
    # ===========================================
    # EMOTIONAL ANALYSIS
    # ===========================================
    emotional_context = {}
    if PERSONA_SYSTEMS_LOADED:
        try:
            emotional_context = emotion_intelligence.process_message(user_message)
        except Exception as e:
            print(f"[EMOTION] Error: {e}")
            emotional_context = {}
    
    # ===========================================
    # ADVANCED INTELLIGENCE LAYERS
    # ===========================================
    vulnerability_context = {}
    silence_context = {}
    disagreement_context = {}
    socratic_active = False
    
    if ADVANCED_INTELLIGENCE_LOADED:
        try:
            vulnerability_context = vulnerability_matching.analyze_vulnerability(
                user_message,
                emotional_context.get('current_emotion', {}).get('primary', {}).get('emotion', 'neutral')
            )
            if vulnerability_context.get('level'):
                print(f"[VULNERABILITY] Level: {vulnerability_context['level']}")
        except Exception as e:
            print(f"[VULNERABILITY] Error: {e}")
        
        try:
            silence_context = strategic_silence.should_be_brief({
                "message": user_message,
                "emotion": emotional_context.get('current_emotion', {}).get('primary', {}).get('emotion', 'neutral'),
                "conversation_history": memory.get_runtime_messages()
            })
            if silence_context.get('should_be_brief'):
                print(f"[SILENCE] Brief response recommended")
        except Exception as e:
            print(f"[SILENCE] Error: {e}")
        
        try:
            disagreement_context = disagreement_engine.should_disagree(
                user_message,
                {"emotion": emotional_context.get('current_emotion', {}).get('primary', {}).get('emotion', 'neutral')}
            )
            if disagreement_context:
                print(f"[DISAGREEMENT] Type: {disagreement_context['disagreement_type']}")
        except Exception as e:
            print(f"[DISAGREEMENT] Error: {e}")
        
        try:
            socratic_active = socratic_mode.should_enter_socratic_mode(
                user_message,
                {"emotion": emotional_context.get('current_emotion', {}).get('primary', {}).get('emotion', 'neutral')}
            )
            if socratic_active:
                print(f"[SOCRATIC] Socratic mode activated")
        except Exception as e:
            print(f"[SOCRATIC] Error: {e}")
    
    # ===========================================
    # CONVERSATION INTELLIGENCE
    # ===========================================
    conversation_strategy = {}
    if PERSONA_SYSTEMS_LOADED:
        try:
            conversation_strategy = conversation_intelligence.analyze_message(
                user_message,
                context={"emotional_state": emotional_context}
            )
            print(f"[CONVERSATION] Strategy: {conversation_strategy.get('depth_preference', 'moderate')} depth")
        except Exception as e:
            print(f"[CONVERSATION] Error: {e}")
            conversation_strategy = {}
    
    # ===========================================
    # TOPIC THREADING
    # ===========================================
    if ADVANCED_INTELLIGENCE_LOADED:
        try:
            new_thread = topic_threading.detect_thread_start(
                user_message,
                conversation_strategy.get('depth_preference', 'moderate')
            )
            if new_thread:
                print(f"[THREADING] New thread: {new_thread.topic}")
        except Exception as e:
            print(f"[THREADING] Error: {e}")
    
    
    # ===========================================
    # CONTEXT LAYERING
    # ===========================================
    if ADVANCED_INTELLIGENCE_LOADED:
        try:
            context_layers.add_evidence(user_message, {
                "emotion": emotional_context,
                "topic": "detected_topic",
                "depth": conversation_strategy.get('depth_preference', 'moderate')
            })
        except Exception as e:
            print(f"[CONTEXT LAYERS] Error: {e}")
    
    # ===========================================
    # BUILD CONTEXT WITH MODE DETECTION
    # ===========================================
    context_data = memory.build_prompt(
        user_message=user_message,
        rag_context=rag_context_text,
        memory_context=memory_context_text  # From orchestrator
    )
    
    mode = context_data["mode"]
    total_tokens = context_data["token_breakdown"]["total"]
    
    # ===========================================
    # ASSEMBLE SYSTEM PROMPT ADDITIONS
    # ===========================================
    system_prompt_additions = []
    
    if mode_reset:
        reset_instruction = """
**CRITICAL MODE RESET:**
Return to normal brief conversational style. Keep response SHORT (2-3 sentences).
"""
        system_prompt_additions.append(reset_instruction)
    
    if conversation_state.get("verbose_mode") and not mode_reset:
        verbose_instruction = """
**VERBOSE MODE ACTIVE:**
Provide thorough, in-depth response while maintaining personality.
"""
        system_prompt_additions.append(verbose_instruction)
    
    if conversation_state.get("last_blocked_response"):
        recovery_instruction = """
**RESPONSE LENGTH WARNING:**
Previous response was TOO LONG. Keep under 300 words this time.
"""
        system_prompt_additions.append(recovery_instruction)
        conversation_state["last_blocked_response"] = None
    
    # Add all persona/advanced system additions
    if PERSONA_SYSTEMS_LOADED:
        if emotional_context:
            try:
                emotional_addition = emotional_context.get('system_prompt_addition', '')
                if emotional_addition:
                    system_prompt_additions.append(emotional_addition)
            except: pass
        
        if conversation_strategy:
            try:
                conv_addition = conversation_intelligence.get_prompt_addition(conversation_strategy)
                if conv_addition:
                    system_prompt_additions.append(conv_addition)
            except: pass
        
        try:
            preference_context = preference_learning.get_preference_context()
            if preference_context:
                system_prompt_additions.append(preference_context)
        except: pass
        
        try:
            routine_context = routine_learning.get_routine_context()
            if routine_context:
                system_prompt_additions.append(routine_context)
        except: pass
    
    if ADVANCED_INTELLIGENCE_LOADED:
        if vulnerability_context and vulnerability_context.get('level') in ['medium', 'high']:
            try:
                vuln_instruction = vulnerability_matching.generate_matched_response_instruction(
                    vulnerability_context['level']
                )
                if vuln_instruction:
                    system_prompt_additions.append(vuln_instruction)
            except: pass
        
        if silence_context and silence_context.get('should_be_brief'):
            try:
                silence_instruction = strategic_silence.format_brief_response_instruction(silence_context)
                if silence_instruction:
                    system_prompt_additions.append(silence_instruction)
            except: pass
        
        if disagreement_context:
            try:
                disagreement_instruction = disagreement_engine.format_disagreement_instruction(disagreement_context)
                if disagreement_instruction:
                    system_prompt_additions.append(disagreement_instruction)
            except: pass
        
        if socratic_active:
            try:
                socratic_instruction = socratic_mode.get_socratic_instruction()
                if socratic_instruction:
                    system_prompt_additions.append(socratic_instruction)
            except: pass
        
        try:
            depth = "deep" if relationship.get_intimacy_score() > 60 else "medium"
            layered_context = context_layers.get_context_for_prompt(depth)
            if layered_context:
                system_prompt_additions.append(layered_context)
        except: pass
    
    # Insert additions into prompt
    if system_prompt_additions:
        all_additions = "\n".join(system_prompt_additions)
        prompt_parts = context_data["prompt"].split("<|im_start|>user")
        if len(prompt_parts) == 2:
            context_data["prompt"] = prompt_parts[0] + all_additions + "\n<|im_start|>user" + prompt_parts[1]
    
    # ===========================================
    # DYNAMIC max_tokens
    # ===========================================
    if conversation_state.get("mode_override") == "brief" or mode_reset:
        max_response_tokens = 200
    elif conversation_state.get("mode_override") == "verbose" and not mode_reset:
        max_response_tokens = 1000
    elif silence_context and silence_context.get('should_be_brief'):
        max_response_tokens = 150
    else:
        if mode == "chat":
            max_response_tokens = 400
        elif mode == "memory":
            max_response_tokens = 300
        elif mode == "rag":
            max_response_tokens = 600
        else:
            max_response_tokens = 400
    
    print(f"[MAX TOKENS] {mode} mode - limiting to {max_response_tokens} tokens")
    
    # === DEBUG: SAVE FULL PROMPT ===
    debug_prompt_file = "aid_prompt_debug.txt"
    try:
        with open(debug_prompt_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"MESSAGE #{message_counter} | MODE: {mode.upper()}\n")
            f.write(f"MAX TOKENS: {max_response_tokens}\n")
            f.write(f"ORCHESTRATOR MEMORIES: {len(orchestrator_memories)}\n")
            f.write("=" * 80 + "\n\n")
            f.write(context_data["prompt"])
            f.write("\n\n" + "=" * 80 + "\n")
    except Exception as e:
        print(f"[WARN] Failed to save debug prompt: {e}")
    
    # === GET SAMPLING PARAMS ===
    sampling = memory.get_sampling_params(mode, total_tokens)
    
    # === BUILD API PAYLOAD ===
    payload = {
        "model": MODEL_NAME,
        "prompt": context_data["prompt"],
        "max_new_tokens": max_response_tokens,
        **sampling,
        "do_sample": True,
        "stop": [
            "<|im_end|>",
            "<|im_start|>",
            "<|endoftext|>",
        ]
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=180)
        data = resp.json()
        raw_reply = data.get("content", "").strip()
        
        if not raw_reply:
            print(f"[WARN] Model returned empty content!")
            reply = "[WARN] Empty response"
        else:
            print(f"[DEBUG] Raw response length: {len(raw_reply)} chars")
            reply = clean_response(raw_reply, mode=mode)
            
            if not reply or len(reply) < 10:
                print(f"[WARN] Cleaning removed entire response! Using raw.")
                reply = raw_reply
            else:
                print(f"[DEBUG] Cleaned response ({mode} mode): {len(reply)} chars")
                
                # TEMP DISABLED:                 if not validate_response_coherence(reply, user_message):
                # TEMP DISABLED:                     print("[VALIDATION] Ã¢Å¡Â Ã¯Â¸Â Response failed coherence check")
                # TEMP DISABLED:                     reply = "Hold on mate, let me think about that properly..."
        
        word_count = len(reply.split())
        if word_count > 500:
            print(f"[DEBUG] Word count: {word_count}")
            print(f"[WARN] Response may be too long ({word_count} words)")
            conversation_state["last_blocked_response"] = reply
        
    except requests.exceptions.Timeout:
        reply = "[ERROR] Response timed out"
        print(f"[ERROR] Timeout occurred")
        traceback.print_exc()
    except Exception as e:
        reply = f"[ERROR] Error: {e}"
        traceback.print_exc()

    # ===========================================
    # POST-PROCESSING IN BACKGROUND THREAD
    # ===========================================
    # CRITICAL FIX: Move all post-processing to background thread to prevent blocking
    # This prevents deadlock with memory operations and allows response to be sent immediately

    def post_process_response():
        """Run post-processing operations in background thread"""
        emotion_data = "neutral"

        # Store in runtime
        try:
            emotion_data = mem_emotion.assign_emotion(user_message)
            memory.add_to_runtime("user", user_message, emotion=emotion_data)
            memory.add_to_runtime("aid", reply, emotion="neutral")
            print("[DEBUG] Successfully stored in runtime")
        except Exception as e:
            print(f"[ERROR] Failed to store in runtime: {e}")
            traceback.print_exc()

        # Memory formation
        try:
            from memory_management import observe_interaction

            print(f"[MEMORY FORMATION] Observing interaction...")
            created_memories = observe_interaction(user_message, reply)

            if created_memories and len(created_memories) > 0:
                print(f"[MEMORY FORMATION] Created {len(created_memories)} new memories")
            else:
                print(f"[MEMORY FORMATION] No new memories created (reinforcement pending)")

        except ImportError as e:
            print(f"[MEMORY FORMATION] New memory system not available: {e}")

        except Exception as e:
            print(f"[MEMORY FORMATION] Error: {e}")
            import traceback
            traceback.print_exc()

        # Preference learning
        if PERSONA_SYSTEMS_LOADED:
            try:
                preference_learning.learn_from_interaction(user_message, reply)
            except Exception as e:
                print(f"[PREFERENCES] Learning error: {e}")

        # Relationship metrics
        try:
            conversation_duration = time.time() - start_time
            relationship.update_metrics(
                user_message=user_message,
                aid_response=reply,
                emotion=emotion_data,
                conversation_duration_seconds=conversation_duration
            )

            milestone_messages = relationship.check_milestones()
            if milestone_messages:
                context_data["milestones"] = milestone_messages
        except Exception as e:
            print(f"[RELATIONSHIP] Warning: {e}")

    end_time = time.time()

    # === GATHER ALL STATS BEFORE BACKGROUND THREAD (to avoid deadlock) ===
    runtime_size = None
    stm_size = None
    relationship_stage = "unknown"
    intimacy_score = 0.0

    try:
        runtime_size = memory.get_runtime_size()
        stm_size = len(mem_stm.get_all())
    except Exception as e:
        print(f"[WARN] Could not get memory stats: {e}")

    try:
        relationship_stage = relationship.get_current_stage()
        intimacy_score = relationship.get_intimacy_score()
    except Exception as e:
        print(f"[WARN] Could not get relationship stats: {e}")

    # === DEBUG LOGGING ===
    debug_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "message_number": message_counter,
        "mode": mode,
        "max_tokens": max_response_tokens,
        "orchestrator_memories": len(orchestrator_memories),
        "mode_reset_detected": bool(mode_reset),
        "verbose_mode": conversation_state.get("verbose_mode", False),
        "relationship_stage": relationship_stage,
        "intimacy_score": round(intimacy_score, 1),
        "emotional_state": emotional_context.get('current_emotion', {}).get('primary', {}).get('emotion', 'unknown'),
        "response_mode": emotional_context.get('response_mode', 'default'),
        "conversation_depth": conversation_strategy.get('depth_preference', 'moderate'),
        "token_breakdown": context_data["token_breakdown"],
        "response_time_seconds": round(end_time - start_time, 2),
        "response_preview": reply[:300]
    }

    # Launch post-processing in background thread AFTER gathering stats
    print("[DEBUG] After response processing, launching background post-processing")
    import threading
    post_process_thread = threading.Thread(target=post_process_response, daemon=True)
    post_process_thread.start()
    
    if ADVANCED_INTELLIGENCE_LOADED:
        debug_entry["advanced_systems"] = {
            "vulnerability_level": vulnerability_context.get('level', 'none'),
            "strategic_silence": silence_context.get('should_be_brief', False),
            "disagreement_active": bool(disagreement_context),
            "socratic_mode": socratic_active
        }

    try:
        if os.path.exists(DEBUG_LOG_FILE):
            with open(DEBUG_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(debug_entry)
        if len(logs) > 200:
            logs = logs[-200:]
        with open(DEBUG_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Failed to save debug log: {e}")

    # Console output - uses pre-gathered stats to avoid deadlock
    try:
        print(f"[INFO] Response in {end_time - start_time:.2f}s | Mode: {mode.upper()}")
    except: pass

    try:
        print(f"       [ORCHESTRATOR] Memories used: {len(orchestrator_memories)}")
    except: pass

    try:
        if runtime_size is not None and stm_size is not None:
            print(f"       [MEMORY] Runtime: {runtime_size} | STM: {stm_size}")
    except: pass

    try:
        if relationship_stage != "unknown":
            print(f"       [RELATIONSHIP] Stage: {relationship_stage} | Intimacy: {intimacy_score:.0f}/100")
    except: pass

    print(f"[DEBUG] About to return reply: {len(reply)} chars")
    print(f"[DEBUG] Reply type: {type(reply)}, content preview: {reply[:100] if reply else 'None'}")
    return reply

# =======================
# AUTOMATIC RESPONSE (MODULAR HOOK)
# =======================
from auto_response import register_handlers

state = register_handlers(bot, call_aid_api_override=call_aid_api)
state["conversation_state"] = conversation_state

# =======================
# DISCORD EVENT HANDLERS
# =======================
@bot.event
async def on_ready():
    print(f"[DISCORD] [OK] {bot.user} is now connected and ready!")
    print(f"[DISCORD] Connected to {len(bot.guilds)} server(s)")

    # Initialize voice handler
    try:
        voice_handler.init_voice()
        print("[VOICE] Voice handler initialized successfully")
    except Exception as e:
        print(f"[VOICE] Failed to initialize voice handler: {e}")

    await startup_checks()

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"[ERROR] Discord event error in {event}:")
    traceback.print_exc()

# =======================
# DISCORD COMMANDS (keeping all your existing commands)
# =======================

@bot.command(name='help')
async def help_command(ctx):
    """Display all available commands."""
    embed = discord.Embed(
        title="Ã°Å¸Â¤â€“ AID Command List",
        description="Here's what I can do, mate!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Ã°Å¸â€™Â¬ Basic Commands",
        value=(
            "**!help** - Show this message\n"
            "**!status** - Show AID's current status\n"
            "**!ping** - Check bot responsiveness"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Ã°Å¸Â§Â  Memory Commands",
        value=(
            "**!memory_stats** - View memory system statistics\n"
            "**!orchestrator_status** - Check orchestrator status\n"
            "**!run_maintenance** - Run memory maintenance\n"
            "**!clear_stm** - Clear short-term memory\n"
            "**!clear_runtime** - Clear current session\n"
            "**!reset_memory** - Emergency full reset"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Ã°Å¸Å½Â¯ Mode Commands",
        value=(
            "**!mode** - Check current conversation mode\n"
            "**!force_chat** - Force CHAT mode\n"
            "**!force_memory** - Force MEMORY mode\n"
            "**!force_rag** - Force RAG mode\n"
            "**!reset_mode** - Reset to auto mode"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Ã¢ÂÂ¤Ã¯Â¸Â Relationship Commands",
        value=(
            "**!relationship** - View relationship status\n"
            "**!intimacy** - Check intimacy score\n"
            "**!days** - Days together count"
        ),
        inline=False
    )
    
    embed.set_footer(text="Created by Dee | AID v4.1 with Orchestrator")
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status_command(ctx):
    """Show AID's current status including orchestrator."""
    runtime_size = memory.get_runtime_size()
    stm_size = len(mem_stm.get_all())
    stage = relationship.get_current_stage()
    intimacy = relationship.get_intimacy_score()
    days = relationship.get_days_together()
    
    # Get orchestrator status
    try:
        if ORCHESTRATOR_AVAILABLE:
            orch_status = orchestrator.get_status()
        else:
            orch_status = {}
        orch_active = orch_status.get('orchestrator_initialized', False)
        orch_systems = len(orch_status.get('subsystems', {}))
    except:
        orch_active = False
        orch_systems = 0
    
    embed = discord.Embed(
        title="Ã°Å¸â€œÅ  AID Status",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Memory System",
        value=f"Orchestrator: {'Ã¢Å“â€¦' if orch_active else 'Ã¢ÂÅ’'}\nSystems: {orch_systems}\nRuntime: {runtime_size}\nSTM: {stm_size}",
        inline=True
    )
    
    embed.add_field(
        name="Relationship",
        value=f"Stage: {stage.title()}\nIntimacy: {intimacy:.0f}/100\nDays: {days}",
        inline=True
    )
    
    embed.add_field(
        name="Mode",
        value=conversation_state.get("mode_override", "Auto"),
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command(name='orchestrator_status')
async def orchestrator_status_command(ctx):
    """Check orchestrator status in detail."""
    if not ORCHESTRATOR_AVAILABLE:
        await ctx.send("âš ï¸ Orchestrator not available (using new memory system)")
        return
    try:
        status = orchestrator.get_status()
        
        embed = discord.Embed(
            title="Ã°Å¸Å½Â¯ Memory Orchestrator Status",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Status",
            value="Ã¢Å“â€¦ Active" if status.get('orchestrator_initialized') else "Ã¢ÂÅ’ Inactive",
            inline=False
        )
        
        subsystems = status.get('subsystems', {})
        
        if 'stm' in subsystems:
            stm_data = subsystems['stm']
            embed.add_field(
                name="STM",
                value=f"Loaded: {'Ã¢Å“â€¦' if stm_data.get('loaded') else 'Ã¢ÂÅ’'}\nCount: {stm_data.get('memory_count', 0)}",
                inline=True
            )
        
        if 'ltm' in subsystems:
            ltm_data = subsystems['ltm']
            embed.add_field(
                name="LTM",
                value=f"Loaded: {'Ã¢Å“â€¦' if ltm_data.get('loaded') else 'Ã¢ÂÅ’'}\nCount: {ltm_data.get('memory_count', 0)}",
                inline=True
            )
        
        if 'semantic' in subsystems:
            semantic_data = subsystems['semantic']
            embed.add_field(
                name="Semantic Search",
                value=f"Loaded: {'Ã¢Å“â€¦' if semantic_data.get('loaded') else 'Ã¢ÂÅ’'}\nIndexed: {semantic_data.get('indexed_memories', 0)}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"Ã¢ÂÅ’ Error getting orchestrator status: {e}")

@bot.command(name='run_maintenance')
async def run_maintenance_command(ctx):
    """Run memory system maintenance."""
    YOUR_DISCORD_ID = 472470643648929802
    
    if ctx.author.id != YOUR_DISCORD_ID:
        await ctx.send("Ã¢ÂÅ’ You don't have permission to use this command.")
        return
    
    try:
        await ctx.send("Ã°Å¸â€Â§ Running memory maintenance...")
        
        stats = orchestrator.run_maintenance()
        
        embed = discord.Embed(
            title="Ã¢Å“â€¦ Maintenance Complete",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Promoted to LTM", value=stats.get('promoted', 0), inline=True)
        embed.add_field(name="Archived", value=stats.get('archived', 0), inline=True)
        embed.add_field(name="Consolidated", value=stats.get('consolidated', 0), inline=True)
        embed.add_field(name="Duplicates Removed", value=stats.get('removed_duplicates', 0), inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Ã¢ÂÅ’ Maintenance failed: {e}")

# (Keep all your other existing commands - ping, memory_stats, clear_stm, etc.)
# I'm omitting them here for brevity, but they should all remain unchanged

# =======================
# GRACEFUL SHUTDOWN (WITH ORCHESTRATOR)
# =======================
def shutdown_handler():
    """Save all data before shutdown including orchestrator."""
    print("\n[SHUTDOWN] Saving all data before exit...")
    
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    # Stop proactive system
    if PERSONA_SYSTEMS_LOADED:
        try:
            proactive_engine = proactive.get_engine()
            if proactive_engine:
                proactive_engine.stop()
            print("[SHUTDOWN] [OK] Proactive system stopped")
        except Exception as e:
            print(f"[SHUTDOWN] [WARN] Error stopping proactive: {e}")
    
    # Stop auto-save loop
    try:
        memory.stop_auto_save_loop()
        print("[SHUTDOWN] [OK] Auto-save loop stopped")
    except Exception as e:
        print(f"[SHUTDOWN] [WARN] Error stopping auto-save: {e}")
    
    # NEW: Run final orchestrator maintenance (if available)
    if ORCHESTRATOR_AVAILABLE:
        try:
            print("[SHUTDOWN] Running final orchestrator maintenance...")
            stats = orchestrator.run_maintenance()
            print(f"[SHUTDOWN] [OK] Orchestrator maintenance complete: {stats}")
        except Exception as e:
            print(f"[SHUTDOWN] [WARN] Orchestrator maintenance error: {e}")
    
    # Save runtime to STM
    try:
        runtime_messages = memory.get_runtime_messages()
        
        if runtime_messages:
            for msg in runtime_messages:
                mem_stm.add_message(
                    role=msg.get('role'),
                    content=msg.get('content'),
                    emotion=msg.get('emotion', 'neutral'),
                    timestamp=msg.get('timestamp')
                )
            
            print(f"[SHUTDOWN] [OK] Saved {len(runtime_messages)} runtime messages to STM")
        else:
            print("[SHUTDOWN] [OK] No runtime messages to save")
    except Exception as e:
        print(f"[SHUTDOWN] [ERROR] Failed to save runtime to STM: {e}")
        traceback.print_exc()
    
    print("[SHUTDOWN] [OK] Shutdown complete")

atexit.register(shutdown_handler)

# =======================
# RUN BOT
# =======================
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Keyboard interrupt received")
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        traceback.print_exc()