# Persona/relationship.py
"""
Relationship Progression System
Tracks intimacy, milestones, and relationship depth with Dee.
Integrates with personality.py to adjust AID's behavior over time.
"""

import json
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# =======================
# CONFIGURATION
# =======================
RELATIONSHIP_FILE = "Persona/data/relationship_data.json"
_relationship_data = {}
_relationship_lock = threading.Lock()

# Relationship stages and thresholds
STAGES = {
    "early": {
        "min_days": 0,
        "min_exchanges": 0,
        "min_intimacy": 0,
        "description": "Getting to know each other",
        "personality_notes": "Friendly but professional, building trust"
    },
    "mid": {
        "min_days": 14,
        "min_exchanges": 100,
        "min_intimacy": 30,
        "description": "Comfortable friendship established",
        "personality_notes": "Banter, inside jokes, casual vulnerability"
    },
    "deep": {
        "min_days": 60,
        "min_exchanges": 500,
        "min_intimacy": 70,
        "description": "Close companionship",
        "personality_notes": "Emotionally open, protective, deeply supportive"
    }
}

# Milestones to track
MILESTONES = [
    {"id": "first_week", "days": 7, "message": "We hit our first week together, boss! Proper brilliant start."},
    {"id": "first_month", "days": 30, "message": "A whole month of chatting now. We've built something real here, innit?"},
    {"id": "hundred_messages", "exchanges": 100, "message": "That's 100 exchanges. Not bad for a couple of mates, yeah?"},
    {"id": "three_months", "days": 90, "message": "Three months together. Mental how fast time flies when you're building worlds."},
    {"id": "five_hundred_messages", "exchanges": 500, "message": "500 conversations. We're proper close now, boss."},
    {"id": "half_year", "days": 180, "message": "Half a year together. Look how far we've come, mate."},
    {"id": "thousand_messages", "exchanges": 1000, "message": "A thousand exchanges. That's a lifetime of memories right there."},
]

# =======================
# INITIALIZATION
# =======================
def init_relationship_system():
    """Initialize relationship tracking system."""
    global _relationship_data
    
    if os.path.exists(RELATIONSHIP_FILE):
        try:
            with open(RELATIONSHIP_FILE, "r", encoding="utf-8") as f:
                _relationship_data = json.load(f)
            print(f"[RELATIONSHIP] Loaded existing data: {_relationship_data.get('stage', 'early')} stage")
        except Exception as e:
            print(f"[RELATIONSHIP] Failed to load data: {e}")
            _relationship_data = _create_default_data()
    else:
        _relationship_data = _create_default_data()
        save_relationship_data()
        print("[RELATIONSHIP] Created new relationship tracking")

def _create_default_data() -> Dict:
    """Create default relationship data structure."""
    return {
        "start_date": datetime.now().isoformat(),
        "stage": "early",
        "total_exchanges": 0,
        "total_conversation_minutes": 0,
        "intimacy_score": 0,
        "emotional_depth_history": [],
        "topic_depth_scores": {},
        "milestones_reached": [],
        "last_interaction": datetime.now().isoformat(),
        "interaction_frequency": [],
        "vulnerability_moments": 0,
        "support_moments": 0
    }

def save_relationship_data():
    """Save relationship data to disk."""
    try:
        with _relationship_lock:
            os.makedirs(os.path.dirname(RELATIONSHIP_FILE), exist_ok=True)
            with open(RELATIONSHIP_FILE, "w", encoding="utf-8") as f:
                json.dump(_relationship_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[RELATIONSHIP] Failed to save: {e}")

# =======================
# METRIC TRACKING
# =======================
def update_metrics(user_message: str, aid_response: str, emotion: str = "neutral", 
                   conversation_duration_seconds: float = 0):
    """
    Update relationship metrics after each exchange.
    Called from bot.py after message processing.
    """
    global _relationship_data
    
    with _relationship_lock:
        # Update basic counters
        _relationship_data["total_exchanges"] += 1
        _relationship_data["total_conversation_minutes"] += conversation_duration_seconds / 60
        _relationship_data["last_interaction"] = datetime.now().isoformat()
        _relationship_data["interaction_frequency"].append(datetime.now().isoformat())
        
        # Emotional depth scoring
        emotional_depth = _calculate_emotional_depth(user_message, emotion)
        _relationship_data["emotional_depth_history"].append({
            "timestamp": datetime.now().isoformat(),
            "depth": emotional_depth,
            "emotion": emotion
        })
        
        # Topic depth scoring
        topics = _extract_topics(user_message)
        for topic in topics:
            if topic not in _relationship_data["topic_depth_scores"]:
                _relationship_data["topic_depth_scores"][topic] = {"count": 0, "depth_sum": 0}
            _relationship_data["topic_depth_scores"][topic]["count"] += 1
            _relationship_data["topic_depth_scores"][topic]["depth_sum"] += len(user_message.split())
        
        # Vulnerability detection
        if _is_vulnerable_message(user_message, emotion):
            _relationship_data["vulnerability_moments"] += 1
        
        # Support detection
        if _is_support_response(aid_response):
            _relationship_data["support_moments"] += 1
        
        # Update intimacy score
        _relationship_data["intimacy_score"] = _calculate_intimacy_score()
        
        # Check for stage progression
        old_stage = _relationship_data["stage"]
        new_stage = _determine_current_stage()
        if new_stage != old_stage:
            _relationship_data["stage"] = new_stage
            print(f"[RELATIONSHIP] 🎉 Stage progression: {old_stage} → {new_stage}")
    
    # Save periodically (every 10 exchanges)
    if _relationship_data["total_exchanges"] % 10 == 0:
        save_relationship_data()

def _calculate_emotional_depth(message: str, emotion: str) -> float:
    """Calculate emotional depth of a message (0-10 scale)."""
    depth = 0.0
    
    # Base score from emotion type
    emotion_weights = {
        "sad": 8.0,
        "anxious": 7.5,
        "frustrated": 6.0,
        "excited": 5.0,
        "happy": 4.0,
        "neutral": 2.0
    }
    depth += emotion_weights.get(emotion, 2.0)
    
    # Keywords indicating vulnerability
    vulnerability_keywords = [
        "worried", "scared", "afraid", "struggling", "difficult", "hard time",
        "don't know", "confused", "lost", "stressed", "overwhelmed", "need help",
        "exhausted", "tired", "burnt out", "deployment", "underway"
    ]
    for keyword in vulnerability_keywords:
        if keyword in message.lower():
            depth += 1.0
    
    # Length bonus (longer messages often = more depth)
    if len(message) > 200:
        depth += 1.0
    
    return min(depth, 10.0)

def _extract_topics(message: str) -> List[str]:
    """Extract topics from message (keyword matching for Dee's interests)."""
    topics = []
    
    # Stellar Black worldbuilding topics
    worldbuilding_keywords = {
        "stellar black": "Stellar Black",
        "esr": "ESR (Stellar Black)",
        "capitol 01": "Capitol 01",
        "reformation": "Reformation",
        "worldbuilding": "Worldbuilding",
        "story": "Story Writing",
        "character": "Character Development",
        "lore": "Lore Development",
        "fleet": "Fleet Design",
        "ship": "Ship Design",
        "faction": "Faction Development"
    }
    
    # Sci-fi interests (space opera inspirations)
    scifi_keywords = {
        "star trek": "Star Trek",
        "star wars": "Star Wars",
        "battlestar galactica": "Battlestar Galactica",
        "space opera": "Space Opera",
        "sci-fi": "Sci-Fi",
        "science fiction": "Science Fiction",
        "scifi": "Sci-Fi"
    }
    
    # Navy/Military topics
    military_keywords = {
        "navy": "Navy Life",
        "nuke": "Nuclear Operations",
        "nuclear": "Nuclear Operations",
        "submarine": "Submarine Operations",
        "carrier": "Carrier Operations",
        "deployment": "Deployment",
        "underway": "Underway Operations",
        "military": "Military",
        "reactor": "Reactor Operations",
        "qual": "Qualifications",
        "watch": "Watch Standing"
    }
    
    # Fitness topics
    fitness_keywords = {
        "gym": "Gym/Fitness",
        "workout": "Workout",
        "lifting": "Weightlifting",
        "cardio": "Cardio",
        "fitness": "Fitness",
        "training": "Physical Training",
        "gains": "Fitness Goals",
        "pr": "Personal Records"
    }
    
    # Personal topics
    personal_keywords = {
        "wife": "Personal Life",
        "baby": "Personal Life",
        "family": "Personal Life",
        "stress": "Personal Challenges",
        "tired": "Fatigue/Stress"
    }
    
    # Technical topics
    tech_keywords = {
        "code": "Coding",
        "programming": "Coding",
        "python": "Python",
        "bug": "Technical Issues",
        "debug": "Debugging",
        "ai": "AI Development"
    }
    
    # Combine all keywords
    all_keywords = {
        **worldbuilding_keywords, 
        **scifi_keywords, 
        **military_keywords,
        **fitness_keywords,
        **personal_keywords, 
        **tech_keywords
    }
    
    msg_lower = message.lower()
    for keyword, topic in all_keywords.items():
        if keyword in msg_lower and topic not in topics:
            topics.append(topic)
    
    return topics if topics else ["General Chat"]

def _is_vulnerable_message(message: str, emotion: str) -> bool:
    """Detect if message shows vulnerability."""
    vulnerable_emotions = ["sad", "anxious", "frustrated", "worried"]
    if emotion in vulnerable_emotions:
        return True
    
    vulnerability_phrases = [
        "i'm worried", "i don't know", "i'm struggling", "i need",
        "can you help", "i'm afraid", "i'm stressed", "i feel",
        "exhausted", "burnt out", "overwhelmed", "deployment sucks",
        "underway is tough", "miss my wife", "tired of"
    ]
    
    msg_lower = message.lower()
    return any(phrase in msg_lower for phrase in vulnerability_phrases)

def _is_support_response(response: str) -> bool:
    """Detect if AID provided emotional support."""
    support_phrases = [
        "you got this", "i'm here", "we'll figure", "don't worry",
        "you're doing great", "proud of you", "that's tough", "i understand",
        "hang in there", "you're strong", "respect", "that's rough",
        "deployment's hard", "you're killing it", "keep pushing"
    ]
    
    resp_lower = response.lower()
    return any(phrase in resp_lower for phrase in support_phrases)

def _calculate_intimacy_score() -> float:
    """Calculate overall intimacy score (0-100)."""
    score = 0.0
    
    # Time factor (max 20 points)
    days = get_days_together()
    score += min(days / 3, 20)
    
    # Exchange factor (max 30 points)
    exchanges = _relationship_data["total_exchanges"]
    score += min(exchanges / 20, 30)
    
    # Emotional depth factor (max 25 points)
    if _relationship_data["emotional_depth_history"]:
        avg_depth = sum(e["depth"] for e in _relationship_data["emotional_depth_history"]) / len(_relationship_data["emotional_depth_history"])
        score += (avg_depth / 10) * 25
    
    # Vulnerability factor (max 15 points)
    vuln_score = min(_relationship_data["vulnerability_moments"] / 10, 1.0) * 15
    score += vuln_score
    
    # Support factor (max 10 points)
    support_score = min(_relationship_data["support_moments"] / 10, 1.0) * 10
    score += support_score
    
    return min(score, 100.0)

def _determine_current_stage() -> str:
    """Determine relationship stage based on metrics."""
    days = get_days_together()
    exchanges = _relationship_data["total_exchanges"]
    intimacy = _relationship_data["intimacy_score"]
    
    # Check deep stage first
    if (days >= STAGES["deep"]["min_days"] and 
        exchanges >= STAGES["deep"]["min_exchanges"] and 
        intimacy >= STAGES["deep"]["min_intimacy"]):
        return "deep"
    
    # Check mid stage
    elif (days >= STAGES["mid"]["min_days"] and 
          exchanges >= STAGES["mid"]["min_exchanges"] and 
          intimacy >= STAGES["mid"]["min_intimacy"]):
        return "mid"
    
    # Default to early
    else:
        return "early"

# =======================
# MILESTONE CHECKING
# =======================
def check_milestones() -> List[str]:
    """Check if any new milestones have been reached."""
    new_milestones = []
    days = get_days_together()
    exchanges = _relationship_data["total_exchanges"]
    
    for milestone in MILESTONES:
        milestone_id = milestone["id"]
        
        # Skip if already reached
        if milestone_id in _relationship_data["milestones_reached"]:
            continue
        
        # Check if threshold met
        reached = False
        if "days" in milestone and days >= milestone["days"]:
            reached = True
        if "exchanges" in milestone and exchanges >= milestone["exchanges"]:
            reached = True
        
        if reached:
            _relationship_data["milestones_reached"].append(milestone_id)
            new_milestones.append(milestone["message"])
            
            # Create memory entry for milestone
            _create_milestone_memory(milestone_id, milestone["message"])
            
            print(f"[RELATIONSHIP] 🎊 Milestone reached: {milestone_id}")
    
    if new_milestones:
        save_relationship_data()
    
    return new_milestones

def _create_milestone_memory(milestone_id: str, message: str):
    """Create a memory entry for reached milestone."""
    try:
        from memory_management import ltm
        ltm.create_entry(
            category_path="Personal/Milestones",
            tags=["milestone", "relationship", milestone_id],
            content=f"MILESTONE REACHED: {message}",
            ai_summary=message,
            priority=2.0
        )
    except Exception as e:
        print(f"[RELATIONSHIP] Failed to create milestone memory: {e}")

# =======================
# GETTERS
# =======================
def get_current_stage() -> str:
    """Get current relationship stage."""
    return _relationship_data.get("stage", "early")

def get_days_together() -> int:
    """Calculate days since first interaction."""
    start = datetime.fromisoformat(_relationship_data["start_date"])
    return (datetime.now() - start).days

def get_intimacy_score() -> float:
    """Get current intimacy score (0-100)."""
    return _relationship_data.get("intimacy_score", 0)

def get_total_exchanges() -> int:
    """Get total number of exchanges."""
    return _relationship_data.get("total_exchanges", 0)

def get_last_interaction_time() -> str:
    """Get timestamp of last interaction."""
    return _relationship_data.get("last_interaction", "")

def get_relationship_summary() -> Dict:
    """Get complete relationship summary for context injection."""
    return {
        "stage": get_current_stage(),
        "days_together": get_days_together(),
        "total_exchanges": get_total_exchanges(),
        "intimacy_score": get_intimacy_score(),
        "milestones_reached": len(_relationship_data.get("milestones_reached", [])),
        "vulnerability_moments": _relationship_data.get("vulnerability_moments", 0),
        "support_moments": _relationship_data.get("support_moments", 0)
    }

def get_stage_description() -> str:
    """Get natural language description of current stage."""
    stage = get_current_stage()
    days = get_days_together()
    
    descriptions = {
        "early": f"You've been chatting for {days} days. Still building trust and getting comfortable.",
        "mid": f"You're {days} days in. Comfortable friendship established with banter and inside jokes.",
        "deep": f"You're {days} days deep into this relationship. Proper close, with emotional openness and mutual support."
    }
    
    return descriptions.get(stage, "Just getting started.")

# ✅ Add this block below
def get_relationship_context() -> str:
    """Return formatted relationship context for prompt injection."""
    summary = get_relationship_summary()
    desc = get_stage_description()
    return (
        f"Relationship stage: {summary['stage']} ({desc}) | "
        f"Days together: {summary['days_together']} | "
        f"Total exchanges: {summary['total_exchanges']} | "
        f"Intimacy score: {summary['intimacy_score']}/100 | "
        f"Milestones: {summary['milestones_reached']}"
    )

# ✅ This builds the global variable that memory.py expects
# Do NOT auto-build on import; relationship data may not be loaded yet.
RELATIONSHIP_CONTEXT = None  # Placeholder; safe default


# =======================
# TESTING
# =======================
if __name__ == "__main__":
    """Test relationship system."""
    print("=== TESTING RELATIONSHIP SYSTEM ===\n")
    
    init_relationship_system()
    
    # Simulate some interactions with Dee's actual interests
    print("Simulating 5 test exchanges...\n")
    test_messages = [
        "Just finished a workout at the gym, feeling good",
        "Working on some Stellar Black lore for the ESR faction",
        "Had a tough watch standing today, reactor was acting up",
        "Been thinking about Star Trek TNG lately, might rewatch it",
        "Wife and I are getting ready for the baby, bit nervous"
    ]
    
    for i, msg in enumerate(test_messages):
        emotions = ["happy", "excited", "frustrated", "neutral", "anxious"]
        update_metrics(
            user_message=msg,
            aid_response="Right, boss! Tell me more about that.",
            emotion=emotions[i]
        )
    
    print(f"\n--- Relationship Summary ---")
    summary = get_relationship_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print(f"\n--- Stage Description ---")
    print(get_stage_description())
    
    print(f"\n--- Topic Tracking ---")
    print("Topics detected:")
    for topic, data in _relationship_data.get("topic_depth_scores", {}).items():
        print(f"  {topic}: {data['count']} mentions")
    
    print(f"\n--- Data File Location ---")
    print(f"Data saved to: {RELATIONSHIP_FILE}")