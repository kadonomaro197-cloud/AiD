import os
import json
import faiss
import asyncio
import numpy as np
from sentence_transformers import SentenceTransformer

# Globals
embedding_model = None
faiss_index = None
metadata_obj = None
model_loaded_event = asyncio.Event()


# ----------------------------
# Load FAISS index + metadata
# ----------------------------
def load_index(index_file, metadata_file):
    """Load FAISS index and metadata for a given dataset."""
    global faiss_index, metadata_obj

    if not os.path.exists(index_file):
        raise FileNotFoundError(f"FAISS index not found: {index_file}")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

    print(f"[INFO] Loading FAISS index from {index_file}...")
    faiss_index = faiss.read_index(index_file)
    print(f"[INFO] Loaded FAISS index with {faiss_index.ntotal} vectors.")

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata_obj = json.load(f)
    print(f"[INFO] Loaded metadata for {len(metadata_obj)} paragraphs.")

    return faiss_index, metadata_obj


# ----------------------------
# Load embedding model
# ----------------------------
async def load_embedding_model(model_name="all-MiniLM-L6-v2"):
    """Load the embedding model asynchronously."""
    global embedding_model
    print("[INFO] Loading embedding model...")

    loop = asyncio.get_event_loop()
    embedding_model = await loop.run_in_executor(None, SentenceTransformer, model_name)

    print("[INFO] Embedding model loaded.")
    model_loaded_event.set()


# ----------------------------
# Query FAISS index
# ----------------------------
def query_database(query, top_k=5, faiss_index_override=None, metadata_override=None):
    """Search the FAISS index for the query and return top results."""
    global embedding_model, faiss_index, metadata_obj

    if embedding_model is None:
        raise RuntimeError("Embedding model not loaded yet.")

    # Allow overrides (so you can pass custom index/metadata from test script)
    index = faiss_index_override or faiss_index
    meta = metadata_override or metadata_obj

    if index is None or meta is None:
        raise RuntimeError("Index and metadata must be loaded before querying.")

    # Encode query → vector
    query_vec = embedding_model.encode([query])
    query_vec = np.array(query_vec).astype("float32")

    # Search FAISS
    distances, indices = index.search(query_vec, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if 0 <= idx < len(meta):
            results.append({
                "title": meta[idx].get("title", "Untitled"),
                "text": meta[idx].get("text", ""),
                "score": float(dist)
            })

    return results
