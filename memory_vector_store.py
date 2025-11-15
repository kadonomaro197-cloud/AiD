# memory_management/memory_vector_store.py
"""
FAISS-based vector store for AiD's memory system.
Handles storage, persistence, and semantic search for all memories.
"""

import faiss
import numpy as np
import json
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer
from pathlib import Path
import threading
from typing import List, Optional

class MemoryVectorStore:
    """
    FAISS vector store for memory embeddings with metadata.
    Each memory has: content, embedding, timestamp, last_accessed, 
    access_count, importance, entities
    """
    
    def __init__(self, data_dir="memory_management/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.index_path = self.data_dir / "memory_index.faiss"
        self.metadata_path = self.data_dir / "memory_metadata.json"
        
        # Initialize embedding model (same as RAG system)
        print("[MEMORY STORE] Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        # Load or create index
        self.index = None
        self.memories = []
        self.load_or_create_index()
        
        print(f"[MEMORY STORE] Initialized with {len(self.memories)} memories")

    def _encode_with_timeout(self, texts: List[str], timeout: float = 5.0) -> Optional[np.ndarray]:
        """
        Encode text with timeout protection to prevent hanging.

        Args:
            texts: List of text strings to encode
            timeout: Maximum seconds to wait (default: 5.0)

        Returns:
            Embedding array or None if timeout
        """
        result = [None]
        exception = [None]

        def encode_task():
            try:
                result[0] = self.embedding_model.encode(texts)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=encode_task, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            print(f"[MEMORY STORE] WARNING: Embedding timeout after {timeout}s")
            return None

        if exception[0]:
            print(f"[MEMORY STORE] ERROR: Embedding failed: {exception[0]}")
            return None

        return result[0]

    def add_memory(self, content, timestamp=None, importance=1.0, entities=None):
        """
        Add a new memory to the vector store.
        
        Args:
            content: Memory text content
            timestamp: When memory was created (defaults to now)
            importance: Importance multiplier (1.0-2.5)
            entities: List of extracted entities (proper nouns)
        
        Returns:
            Memory ID (index in memories list)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if entities is None:
            entities = []

        # Create embedding with timeout protection
        embeddings = self._encode_with_timeout([content], timeout=5.0)
        if embeddings is None:
            print(f"[MEMORY STORE] ERROR: Failed to create embedding for memory, skipping")
            return None

        embedding = embeddings[0]

        # Create memory object
        memory = {
            "id": len(self.memories),
            "content": content,
            "timestamp": timestamp.isoformat(),
            "last_accessed": timestamp.isoformat(),
            "access_count": 1,
            "importance": importance,
            "entities": entities
        }
        
        # Add to FAISS index
        embedding_np = np.array([embedding], dtype='float32')
        self.index.add(embedding_np)
        
        # Add metadata
        self.memories.append(memory)
        
        print(f"[MEMORY STORE] Added memory #{memory['id']}: {content[:50]}...")
        
        return memory['id']
    
    def search(self, query, top_k=50):
        """
        Semantic search for relevant memories.
        Returns top_k candidates with similarity scores.
        
        Args:
            query: Search query text
            top_k: Number of candidates to return
        
        Returns:
            List of (memory, similarity_score) tuples
        """
        if len(self.memories) == 0:
            return []

        # Embed query with timeout protection
        query_embeddings = self._encode_with_timeout([query], timeout=5.0)
        if query_embeddings is None:
            print(f"[MEMORY STORE] ERROR: Failed to encode search query, returning empty results")
            return []

        query_vector = query_embeddings[0]
        query_np = np.array([query_vector], dtype='float32')
        
        # Search FAISS (returns distances, need to convert to similarities)
        k = min(top_k, len(self.memories))
        distances, indices = self.index.search(query_np, k)
        
        # Convert L2 distances to similarity scores (0-1 range)
        # L2 distance: 0 = identical, higher = less similar
        # Convert to similarity: 1 / (1 + distance)
        similarities = 1 / (1 + distances[0])
        
        # Build results
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if idx < len(self.memories):  # Safety check
                memory = self.memories[idx].copy()
                results.append((memory, float(similarity)))
        
        return results
    
    def update_access_stats(self, memory_id):
        """
        Update access statistics for a memory.
        Called when memory is retrieved and used.
        """
        if 0 <= memory_id < len(self.memories):
            self.memories[memory_id]["access_count"] += 1
            self.memories[memory_id]["last_accessed"] = datetime.now().isoformat()
    
    def get_memory(self, memory_id):
        """Get a specific memory by ID"""
        if 0 <= memory_id < len(self.memories):
            return self.memories[memory_id]
        return None
    
    def get_all_memories(self):
        """Get all memories (for debugging/analysis)"""
        return self.memories.copy()
    
    def save_index(self):
        """Persist FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
            
            print(f"[MEMORY STORE] Saved {len(self.memories)} memories to disk")
            return True
        except Exception as e:
            print(f"[MEMORY STORE] ERROR saving index: {e}")
            return False
    
    def load_or_create_index(self):
        """Load existing index from disk or create new one"""
        try:
            if self.index_path.exists() and self.metadata_path.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_path))
                
                # Load metadata
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
                
                print(f"[MEMORY STORE] Loaded {len(self.memories)} memories from disk")
            else:
                # Create new index
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.memories = []
                print("[MEMORY STORE] Created new empty index")
        except Exception as e:
            print(f"[MEMORY STORE] ERROR loading index: {e}")
            print("[MEMORY STORE] Creating new index instead")
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.memories = []
    
    def get_stats(self):
        """Get statistics about the memory store"""
        if not self.memories:
            return {
                "total_memories": 0,
                "total_accesses": 0,
                "avg_accesses": 0
            }
        
        total_accesses = sum(m["access_count"] for m in self.memories)
        
        return {
            "total_memories": len(self.memories),
            "total_accesses": total_accesses,
            "avg_accesses": total_accesses / len(self.memories) if self.memories else 0,
            "index_size": self.index.ntotal
        }

# Global instance
_memory_store = None

def get_memory_store():
    """Get or create global memory store instance"""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryVectorStore()
    return _memory_store