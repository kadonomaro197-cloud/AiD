# memory_management/utils.py

import os
import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =======================
# Unique Memory ID
# =======================
def generate_mem_id(mem_file=None):
    """
    Generate a unique memory ID in the form MEM-YYYYMMDD-###.
    Uses a JSON file to keep track of daily counts.
    
    mem_file: optional path to mem_ids.json. Defaults to "memory_management/backups/mem_ids.json".
    """
    today = datetime.now().strftime("%Y%m%d")
    if mem_file is None:
        mem_file = "memory_management/backups/mem_ids.json"

    ids = load_json(mem_file, default={})
    count = ids.get(today, 0) + 1
    ids[today] = count
    save_json(mem_file, ids)

    return f"MEM-{today}-{str(count).zfill(3)}"


# =======================
# Similarity Scoring
# =======================
def compute_similarity(text1, text2):
    """
    Return a similarity score (0–1) between two text strings using TF-IDF + cosine similarity.
    Purely a helper; does NOT perform memory retrieval.
    """
    if not text1 or not text2:
        return 0.0
    vectorizer = TfidfVectorizer().fit([text1, text2])
    tfidf_matrix = vectorizer.transform([text1, text2])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(score)


# =======================
# Token Approximation
# =======================
def truncate_to_tokens(text, max_tokens):
    """
    Approximate token truncation by word count.
    Assumes 1 token ≈ 0.75 words.
    Purely utility; does not make memory decisions.
    """
    words = text.split()
    approx_tokens = int(len(words) * 0.75)
    if approx_tokens > max_tokens:
        allowed_words = int(max_tokens / 0.75)
        return " ".join(words[-allowed_words:])
    return text


# =======================
# Timestamp Helper
# =======================
def current_timestamp():
    """
    Return current timestamp as ISO string with seconds precision.
    """
    return datetime.now().isoformat(timespec="seconds")


# =======================
# JSON Load / Save Helpers
# =======================
def save_json(file_path, data):
    """
    Save data to JSON safely. Creates directories if needed.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[UTILS] Failed to save JSON to {file_path}: {e}")


def load_json(file_path, default=None):
    """
    Load JSON file safely. Returns default if file not found.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[UTILS] Failed to load JSON from {file_path}: {e}")
            return default if default is not None else {}
    return default if default is not None else {}


# =======================
# Category Management
# =======================
def get_or_create_categories(file_path="memory_management/backups/categories.json"):
    """
    Load existing categories or create default ones ('project', 'personal').
    Allows dynamic addition of new categories later.
    Returns full hierarchical path dict.
    """
    categories = load_json(file_path, default=None)
    if not categories:
        categories = {
            "Project": {},
            "Personal": {}
        }
        save_json(file_path, categories)
    return categories


def add_category(name, parent=None, file_path="memory_management/backups/categories.json"):
    """
    Add a new category if it doesn’t exist.
    If parent is provided, adds it under that parent.
    """
    categories = get_or_create_categories(file_path)
    if parent:
        if parent not in categories:
            categories[parent] = {}
        if name not in categories[parent]:
            categories[parent][name] = {}
    else:
        if name not in categories:
            categories[name] = {}
    save_json(file_path, categories)
    return categories
