import json
import os
from tqdm import tqdm
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import argparse

# ---------------------------
# ARGUMENTS
# ---------------------------
parser = argparse.ArgumentParser(description="Build FAISS index for a JSONL dataset of paragraphs.")
parser.add_argument(
    "--input_file",
    type=str,
    required=True,
    help="Path to the JSONL file containing paragraphs."
)
parser.add_argument(
    "--index_file",
    type=str,
    default=None,
    help="Path to save FAISS index file. Defaults to <basename>_index.faiss"
)
parser.add_argument(
    "--metadata_file",
    type=str,
    default=None,
    help="Path to save metadata JSON. Defaults to <basename>_metadata.json"
)
parser.add_argument(
    "--embedding_model",
    type=str,
    default="all-MiniLM-L6-v2",
    help="SentenceTransformer model name for embeddings"
)
args = parser.parse_args()

# ---------------------------
# Auto-generate output file names if not provided
# ---------------------------
base_name = os.path.splitext(os.path.basename(args.input_file))[0]

if args.index_file is None:
    args.index_file = f"{base_name}_index.faiss"
if args.metadata_file is None:
    args.metadata_file = f"{base_name}_metadata.json"

# ---------------------------
# 1. Load paragraphs with headers
# ---------------------------
paragraphs = []
metadata = []

with open(args.input_file, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        try:
            obj = json.loads(line)
            text = obj.get("text", "").strip()
            if len(text) < 20:
                continue
            paragraphs.append(text)
            metadata.append({
                "title": obj.get("title", "Untitled"),
                "url": obj.get("url", ""),
                "paragraph_id": obj.get("paragraph_id", line_num),
                "text": text
            })
        except Exception as e:
            print(f"[WARN] Skipping line {line_num} due to error: {e}")

print(f"Loaded {len(paragraphs)} valid paragraphs for FAISS embedding.")

# ---------------------------
# 2. Generate embeddings
# ---------------------------
print(f"Loading embedding model '{args.embedding_model}'...")
model = SentenceTransformer(args.embedding_model)

print("Generating embeddings...")
embeddings = model.encode(
    paragraphs,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

# ---------------------------
# 3. Build FAISS index
# ---------------------------
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # cosine similarity (normalized vectors)
index.add(embeddings)
print(f"FAISS index built with {index.ntotal} vectors.")

# ---------------------------
# 4. Save index & metadata
# ---------------------------
faiss.write_index(index, args.index_file)
with open(args.metadata_file, "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"FAISS index saved at: {args.index_file}")
print(f"Metadata saved at: {args.metadata_file}")
print("✅ All done! AID can now query the updated RAG data.")
