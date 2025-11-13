# rag_query.py
import asyncio
import numpy as np
import traceback

from rag_loader import get_index, load_embedding_model, model_loaded_event, get_embedding_model
from keywords import get_categories_for_query

# =======================
# QUERY DATABASE
# =======================
def query_database(user_query, top_k=5):
    """
    Query the appropriate RAG dataset(s) based on keywords in user_query.
    Returns a list of dicts: [{"title": ..., "text": ...}, ...]
    """
    try:
        embedding_model = get_embedding_model()
        if embedding_model is None:
            raise ValueError("[RAG] Embedding model not loaded!")

        # Convert query to vector
        query_vector = embedding_model.encode([user_query]).astype("float32")

        # Determine which categories to query
        categories_to_query = get_categories_for_query(user_query)

        results = []

        for cat in categories_to_query:
            index, metadata = get_index(cat)
            if not index or not metadata:
                print(f"[WARN] No index or metadata found for category: '{cat}'")
                continue

            # Normalize metadata: ensure all entries are dicts with 'title' and 'text'
            normalized_metadata = []
            for i, entry in enumerate(metadata):
                if isinstance(entry, dict):
                    title = entry.get("title", "Untitled")
                    text = entry.get("text") or entry.get("content") or entry.get("paragraph") or ""
                    normalized_metadata.append({"title": str(title), "text": str(text)})
                elif isinstance(entry, str):
                    normalized_metadata.append({"title": "Untitled", "text": entry})
                else:
                    normalized_metadata.append({"title": "Untitled", "text": str(entry)})

            try:
                D, I = index.search(query_vector, top_k)
                if not isinstance(I, np.ndarray):
                    print(f"[ERROR] FAISS returned non-array indices for category '{cat}': {I}")
                    continue

                # 🔍 Debug: show raw FAISS indices before filtering
                print(f"[DEBUG] FAISS raw indices for category '{cat}': {I[0].tolist()}")

                for idx in I[0]:
                    if not isinstance(idx, (int, np.integer)):
                        print(f"[DEBUG] Skipping non-integer index: {idx}")
                        continue
                    if idx < 0 or idx >= len(normalized_metadata):
                        print(f"[DEBUG] Invalid FAISS index {idx} for category '{cat}', skipping.")
                        continue
                    entry = normalized_metadata[idx]
                    if not isinstance(entry, dict):
                        print(f"[DEBUG] Skipping non-dict metadata entry at index {idx}: {entry}")
                        continue
                    if "text" not in entry or not isinstance(entry["text"], str):
                        print(f"[DEBUG] Skipping metadata entry missing 'text' at index {idx}: {entry}")
                        continue
                    results.append(entry)
            except Exception as e_idx:
                print(f"[ERROR] FAISS index search failed for category '{cat}'")
                traceback.print_exc()

        # 🔍 Debug log to confirm shape and keys of results
        print(f"[DEBUG] query_database returning {len(results)} results from categories: {categories_to_query}")
        for i, r in enumerate(results[:5]):  # only show first 5 for sanity
            print(f"   [{i}] keys={list(r.keys())}, types={{'title': {type(r.get('title'))}, 'text': {type(r.get('text'))}}}")

        return results

    except Exception as e:
        print("[ERROR] RAG query failed in query_database!")
        print("Exception type:", type(e))
        print("Exception message:", e)
        traceback.print_exc()
        return []

# =======================
# BUILD RAG PROMPT
# =======================
def build_rag_prompt(user_query, indexes=None, top_k=5, snippet_length=500):
    """
    Builds a prompt string with RAG results for the given user_query.
    """
    try:
        results = query_database(user_query, top_k=top_k)

        rag_context = []
        for r in results:
            if not isinstance(r, dict):
                print("[DEBUG] Non-dict result in RAG query:", r, type(r))
                continue
            snippet = r.get("text", "")
            if not isinstance(snippet, str):
                print(f"[DEBUG] Non-string 'text' in result: {r}")
                snippet = str(snippet)
            if len(snippet) > snippet_length:
                snippet = snippet[:snippet_length] + "…"
            title = r.get("title", "Untitled")
            if not isinstance(title, str):
                title = str(title)
            rag_context.append(f"Title: {title}\n{snippet}")

        full_prompt = f"Use the following context from the database to answer the question:\n\n"
        full_prompt += "\n\n".join(rag_context)
        full_prompt += f"\n\nQuestion: {user_query}\nAnswer:"
        return full_prompt

    except Exception as e:
        print("[ERROR] Failed to build RAG prompt!")
        print("Exception type:", type(e))
        print("Exception message:", e)
        traceback.print_exc()
        return f"⚠️ Error building RAG prompt: {e}"

# =======================
# ASYNC HELPER
# =======================
async def async_query(user_query, top_k=5):
    """
    Async wrapper for query_database, ensures embedding model is loaded.
    Returns a list of RAG results: [{"title": ..., "text": ...}, ...]
    """
    embedding_model = get_embedding_model()
    if embedding_model is None:
        print("[RAG] Embedding model not loaded yet, waiting...")
        await model_loaded_event.wait()

    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, query_database, user_query, top_k)
    except Exception as e:
        print("[ERROR] Async RAG query failed!")
        print("Exception type:", type(e))
        print("Exception message:", e)
        traceback.print_exc()
        return []
