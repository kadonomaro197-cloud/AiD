import requests
import json
import time
from datetime import datetime

# --- MEMORY DUMMIES ---
short_term_memory = []
long_term_memory = {
    "personal_facts": [],
    "projects": [],
    "general_knowledge": []
}

def add_to_memory(fact):
    """Dummy function for testing, does not persist memory."""
    pass

# --- CONFIG ---
API_URL = "http://127.0.0.1:49936/completions"
MODEL_NAME = "AID"
SHORT_TERM_LIMIT = 50

# --- DIAGNOSTIC CALL FUNCTION ---
def call_aid_api_diagnostic(user_message: str):
    start_time = time.time()
    global short_term_memory

    # Short-term memory trimming
    if len(short_term_memory) > SHORT_TERM_LIMIT:
        summary = " | ".join([f"User: {m['user']}, AID: {m['aid']}"
                              for m in short_term_memory[:SHORT_TERM_LIMIT // 2]])
        short_term_memory = [{"user": "summary", "aid": summary}] + short_term_memory[SHORT_TERM_LIMIT // 2:]

    # Recent conversation context
    recent_context = "\n".join([f"User: {m['user']}\nAID: {m['aid']}" for m in short_term_memory])

    # Top memory facts
    top_memory = []
    for cat in ["personal_facts", "projects", "general_knowledge"]:
        top_memory += long_term_memory[cat][-10:]

    personality_prompt = (
        "Speak in a Cockney-influenced casual accent, friendly but cheeky.\n"
        "Keep responses SHORT (1–3 sentences max).\n"
        "Refer to the user as Dee, Boss, Creator, Sir, or mate.\n"
        "Be helpful, witty, sassy, sarcastic when fitting—but avoid roleplay.\n"
        "Do NOT pretend to be the user or write dialogue for both sides.\n"
        "Keep responses clear, concise, short, and informative.\n"
        "\"hello\": \"'ello\"\n"
        "\"friend\": \"mate\"\n"
        "\"amazing\": \"brill\"\n"
        "\"really\": \"proper\"\n"
        "\"yes\": \"aye\"\n"
        "\"no\": \"nah\"\n"
        "\"great\": \"smashing\"\n"
        "\"ok\": \"alright\"\n"
        "\"thanks\": \"cheers\"\n"
        "\"think\": \"reckon\"\n"
    )

    prompt = (
        personality_prompt +
        f"Long-term memory facts: {json.dumps(top_memory, ensure_ascii=False)}\n\n"
        f"Recent conversation:\n{recent_context}\n\n"
        f"{user_message}\nAID:"
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_new_tokens": 100,
        "temperature": 0.6,
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.3,
        "mirostat_mode": 0,
        "mirostat_tau": 5,
        "mirostat_eta": 0.1,
        "typical_p": 0.95,
        "min_p": 0.05,
        "do_sample": True,
        "stop": ["User:", "\nUser:", "\nAID:"]
    }

    print("[DEBUG] Sending payload to AID API...")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        resp = requests.post(API_URL, json=payload, timeout=300)
        print("[DEBUG] HTTP status code:", resp.status_code)
        data = resp.json()
        print("[DEBUG] Raw response JSON:", json.dumps(data, indent=2, ensure_ascii=False))
        reply = data.get("content", "").strip() or "⚠️ AID responded but returned empty text."
    except Exception as e:
        reply = f"❌ Error connecting to AID API: {e}"

    short_term_memory.append({"user": user_message, "aid": reply})
    if len(short_term_memory) > SHORT_TERM_LIMIT * 2:
        short_term_memory = short_term_memory[-SHORT_TERM_LIMIT:]

    add_to_memory(user_message)
    end_time = time.time()
    print(f"[INFO] Response generated in {end_time - start_time:.2f}s | "
          f"Short-term messages: {len(short_term_memory)} | "
          f"Long-term facts: {sum(len(long_term_memory[c]) for c in long_term_memory)}")
    return reply

# --- RUN TEST ---
if __name__ == "__main__":
    user_input = input("Enter test message for AID: ")
    reply = call_aid_api_diagnostic(user_input)
    print("\n[TEST OUTPUT] AID replied:\n", reply)
