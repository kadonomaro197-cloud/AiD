import json
import os
import time
from datetime import datetime

DEBUG_LOG_FILE = "aid_logs.json"
REFRESH_INTERVAL = 2  # seconds between checks for new logs

def load_logs():
    if not os.path.exists(DEBUG_LOG_FILE):
        return []
    try:
        with open(DEBUG_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
        return logs
    except Exception as e:
        print(f"[ERROR] Failed to read debug log: {e}")
        return []

def display_prompt_viewer(log_entry, is_new=False):
    """Display the full prompt that was sent to the model."""
    if is_new:
        print("\n" + "=" * 100)
        print(">>> NEW PROMPT <<<")
        print("=" * 100)
    
    timestamp = log_entry.get("timestamp", "Unknown")
    message_num = log_entry.get("message_number", "?")
    focus_info = log_entry.get("focus_mode", {})
    
    # Header info
    print(f"\n[TIMESTAMP] {timestamp}")
    print(f"[MESSAGE #] {message_num}")
    print(f"[FOCUS MODE] {'ACTIVE' if focus_info.get('active') else 'Inactive'}")
    if focus_info.get('active'):
        print(f"   └─ Reason: {focus_info.get('reason')}")
        print(f"   └─ Confidence: {focus_info.get('confidence', 0):.0%}")
    
    # Context breakdown
    sliding_window = log_entry.get("sliding_window", {})
    print(f"\n[CONTEXT BREAKDOWN]")
    print(f"   Recent: {sliding_window.get('recent_messages', 0)} msgs ({sliding_window.get('recent_tokens', 0)} tokens)")
    print(f"   Medium: {sliding_window.get('medium_summaries', 0)} summaries ({sliding_window.get('medium_tokens', 0)} tokens)")
    print(f"   Archive: {sliding_window.get('archive_retrieved', 0)} entries ({sliding_window.get('archive_tokens', 0)} tokens)")
    print(f"   RAG: {sliding_window.get('rag_tokens', 0)} tokens")
    print(f"   TOTAL: {sliding_window.get('total_context_tokens', 0)} tokens")
    
    # The full prompt (if available)
    full_prompt = log_entry.get("full_prompt", None)
    if full_prompt:
        print("\n" + "=" * 100)
        print("[FULL PROMPT SENT TO MODEL]")
        print("=" * 100)
        print(full_prompt)
        print("=" * 100)
    else:
        print("\n[WARN] No full prompt captured in this log entry.")
        print("       Add 'full_prompt': final_prompt to debug_entry in bot.py")
    
    # Response preview
    response_preview = log_entry.get("response_preview", "")
    print(f"\n[RESPONSE PREVIEW]")
    print(f"{response_preview}")
    print("\n" + "-" * 100 + "\n")

def monitor_prompts():
    """Monitor and display full prompts in real-time."""
    last_count = 0
    
    print("=" * 100)
    print("AID PROMPT VIEWER - Real-time Prompt Monitor")
    print("=" * 100)
    print("[INFO] Waiting for new prompts...")
    print("[TIP] This shows the FULL prompt AID reads to answer your questions")
    print("=" * 100 + "\n")
    
    while True:
        logs = load_logs()
        if len(logs) > last_count:
            # Clear terminal for fresh display
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("=" * 100)
            print(f"AID PROMPT VIEWER - {len(logs)} Total Prompts Logged")
            print("=" * 100 + "\n")
            
            # Display last 3 entries, marking new ones
            for i, log_entry in enumerate(logs[-3:]):
                is_new = (len(logs) - 3 + i) >= last_count
                display_prompt_viewer(log_entry, is_new=is_new)
            
            # Summary stats
            avg_tokens = sum(entry.get("sliding_window", {}).get("total_context_tokens", 0) for entry in logs) / len(logs)
            print(f"\n[SUMMARY STATS]")
            print(f"   Average Context Size: {avg_tokens:.0f} tokens")
            print(f"   Focus Mode Activations: {sum(1 for e in logs if e.get('focus_mode', {}).get('active'))}")
            print(f"   Most Recent: {logs[-1].get('timestamp', 'N/A')}")
            
            last_count = len(logs)
        
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    monitor_prompts()