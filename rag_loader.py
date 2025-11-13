# rag_loader.py
import os
import json
import faiss
from sentence_transformers import SentenceTransformer
import asyncio  # for model_loaded_event

# --- CONFIGURATION ---
RAG_DATA_PATH = r"C:\Users\DeeDiebS\Desktop\Based\ooga\text-generation-webui\AID-DiscordBot\rag_data"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Global storage for FAISS indexes and metadata
rag_indexes = {}
embedding_model = None

# =======================
# MODEL LOADED EVENT (for bot.py to wait on)
# =======================
model_loaded_event = asyncio.Event()

# =======================
# LOAD EMBEDDING MODEL
# =======================
async def load_embedding_model():
    global embedding_model
    if embedding_model is None:
        print("[RAG] Loading embedding model...")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("[RAG] Embedding model loaded!")
        model_loaded_event.set()  # signal that model is fully loaded

# Getter for embedding model
def get_embedding_model():
    return embedding_model

# =======================
# LOAD FAISS INDEX AND METADATA FOR CATEGORY
# =======================
def load_index_for_category(category_path):
    """
    Loads a FAISS index and metadata from a given category folder.
    Returns (index, metadata_list)
    """
    index_file = None
    metadata_file = None

    # Look for .faiss and metadata.json files
    for file in os.listdir(category_path):
        if file.endswith(".faiss"):
            index_file = os.path.join(category_path, file)
        elif file.endswith("_metadata.json") or file.endswith("metadata.json"):
            metadata_file = os.path.join(category_path, file)

    if not index_file or not metadata_file:
        print(f"[WARN] Missing index or metadata in {category_path}")
        return None, None

    # Load FAISS index
    index = faiss.read_index(index_file)

    # Load metadata
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Normalize metadata: ensure a list of dicts with 'title' and 'text'
    def normalize_entry(entry):
        if isinstance(entry, dict):
            title = entry.get("title", "Untitled")
            text = entry.get("text") or entry.get("content") or entry.get("paragraph") or ""
            return {"title": str(title), "text": str(text)}
        elif isinstance(entry, str):
            return {"title": "Untitled", "text": entry}
        else:
            return {"title": "Untitled", "text": str(entry)}

    # Flatten nested lists and normalize all entries
    def flatten_and_normalize(data):
        flat_list = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list):
                    flat_list.extend(flatten_and_normalize(item))
                else:
                    flat_list.append(normalize_entry(item))
        else:
            flat_list.append(normalize_entry(data))
        return flat_list

    normalized_metadata = flatten_and_normalize(metadata)

    return index, normalized_metadata

# =======================
# LOAD ALL CATEGORIES
# =======================
def load_all_indexes():
    """
    Loads all FAISS indexes and metadata from each category in rag_data/
    Returns a dict: {category_name: {"index": faiss_index, "metadata": metadata_list}}
    """
    global rag_indexes
    rag_indexes = {}

    for entry in os.listdir(RAG_DATA_PATH):
        category_path = os.path.join(RAG_DATA_PATH, entry)
        if not os.path.isdir(category_path):
            continue
        if entry.lower() in ("venv", "__pycache__"):  # skip venv and pycache
            continue

        index, metadata = load_index_for_category(category_path)
        if index is not None and metadata is not None:
            rag_indexes[entry.lower()] = {"index": index, "metadata": metadata}
            print(f"[RAG] Loaded '{entry}' with {len(metadata)} vectors.")

    if rag_indexes:
        total_vectors = sum(len(v["metadata"]) for v in rag_indexes.values())
        categories_loaded = ", ".join(rag_indexes.keys())
        print(f"[RAG] All indexes loaded: {len(rag_indexes)} datasets, {total_vectors} total vectors.")
        print(f"[RAG] Categories: {categories_loaded}")
    print("[RAG] ✅ RAG system fully loaded and ready!")

    return rag_indexes

# =======================
# GET INDEX AND METADATA
# =======================
def get_index(category):
    """
    Returns the FAISS index and metadata for a given category name
    """
    category = category.lower()
    if category in rag_indexes:
        return rag_indexes[category]["index"], rag_indexes[category]["metadata"]
    return None, None
