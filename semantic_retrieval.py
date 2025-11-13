"""
Semantic Retrieval System - Phase 2
Enhanced memory retrieval using semantic understanding and embeddings
"""

import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path

EMBEDDINGS_AVAILABLE = False  # Add this line at module level

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("[WARNING] faiss not installed. Using cosine similarity only.")
    FAISS_AVAILABLE = False


class SemanticRetrieval:
    """
    Semantic memory retrieval using embeddings and FAISS indexing.
    Falls back to keyword search if embeddings unavailable.
    """
    
    def __init__(self, data_dir: str = "memory_management/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model if available
        self.model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[SEMANTIC] Loaded embedding model: all-MiniLM-L6-v2")
            except Exception as e:
                print(f"[SEMANTIC] Could not load embedding model: {e}")
                EMBEDDINGS_AVAILABLE = False
        
        # FAISS index (if available)
        self.index = None
        self.memory_store = []  # List of (memory_dict, embedding) tuples
        self.index_file = self.data_dir / "semantic_index.bin"
        self.store_file = self.data_dir / "memory_store.json"
        
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and memory store."""
        if not FAISS_AVAILABLE or not EMBEDDINGS_AVAILABLE:
            return
        
        try:
            if self.index_file.exists() and self.store_file.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_file))
                
                # Load memory store
                with open(self.store_file, 'r', encoding='utf-8') as f:
                    stored = json.load(f)
                    self.memory_store = [(mem, np.array(emb)) for mem, emb in stored]
                
                print(f"[SEMANTIC] Loaded {len(self.memory_store)} indexed memories")
        except Exception as e:
            print(f"[SEMANTIC] Could not load index: {e}")
            self.index = None
            self.memory_store = []
    
    def _save_index(self):
        """Save FAISS index and memory store."""
        if not FAISS_AVAILABLE or not EMBEDDINGS_AVAILABLE or self.index is None:
            return
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save memory store (convert numpy arrays to lists for JSON)
            stored = [(mem, emb.tolist()) for mem, emb in self.memory_store]
            with open(self.store_file, 'w', encoding='utf-8') as f:
                json.dump(stored, f, indent=2)
            
            print(f"[SEMANTIC] Saved {len(self.memory_store)} indexed memories")
        except Exception as e:
            print(f"[SEMANTIC] Could not save index: {e}")
    
    def add_memory(self, memory: Dict):
        """Add a memory to the semantic index."""
        if not EMBEDDINGS_AVAILABLE or self.model is None:
            return  # Skip if embeddings not available
        
        try:
            # Create searchable text from memory
            search_text = self._memory_to_text(memory)
            
            # Generate embedding
            embedding = self.model.encode(search_text, convert_to_numpy=True)
            
            # Add to FAISS index
            if FAISS_AVAILABLE:
                if self.index is None:
                    # Create new index
                    dim = embedding.shape[0]
                    self.index = faiss.IndexFlatL2(dim)
                
                self.index.add(np.array([embedding]))
            
            # Add to memory store
            self.memory_store.append((memory, embedding))
            
            # Periodic save (every 10 memories)
            if len(self.memory_store) % 10 == 0:
                self._save_index()
        
        except Exception as e:
            print(f"[SEMANTIC] Error adding memory: {e}")
    
    def _memory_to_text(self, memory: Dict) -> str:
        """Convert memory dict to searchable text."""
        parts = []
        
        # Add content
        if 'content' in memory:
            parts.append(memory['content'])
        if 'summary' in memory:
            parts.append(memory['summary'])
        
        # Add metadata
        if 'category' in memory:
            parts.append(f"Category: {memory['category']}")
        if 'tags' in memory and memory['tags']:
            parts.append(f"Tags: {', '.join(memory['tags'])}")
        if 'context' in memory:
            parts.append(memory['context'])
        
        return " ".join(parts)
    
    def search(self, query: str, top_k: int = 5, min_score: float = 0.3) -> List[Tuple[Dict, float]]:
        """
        Semantic search across memories.
        
        Returns:
            List of (memory, similarity_score) tuples, sorted by relevance
        """
        if not EMBEDDINGS_AVAILABLE or self.model is None:
            print("[SEMANTIC] Embeddings unavailable, using keyword fallback")
            return self._keyword_search(query, top_k)
        
        if not self.memory_store:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query, convert_to_numpy=True)
            
            if FAISS_AVAILABLE and self.index is not None:
                # Use FAISS for fast search
                distances, indices = self.index.search(
                    np.array([query_embedding]), 
                    min(top_k * 2, len(self.memory_store))
                )
                
                # Convert distances to similarity scores (L2 -> cosine-like)
                # Lower distance = more similar
                results = []
                for dist, idx in zip(distances[0], indices[0]):
                    if idx < len(self.memory_store):
                        similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity
                        if similarity >= min_score:
                            memory, _ = self.memory_store[idx]
                            results.append((memory, similarity))
                
                return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
            
            else:
                # Fallback: manual cosine similarity
                results = []
                for memory, embedding in self.memory_store:
                    similarity = self._cosine_similarity(query_embedding, embedding)
                    if similarity >= min_score:
                        results.append((memory, similarity))
                
                return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
        
        except Exception as e:
            print(f"[SEMANTIC] Search error: {e}")
            return self._keyword_search(query, top_k)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def _keyword_search(self, query: str, top_k: int) -> List[Tuple[Dict, float]]:
        """Fallback keyword-based search."""
        query_words = set(query.lower().split())
        results = []
        
        for memory, _ in self.memory_store:
            text = self._memory_to_text(memory).lower()
            score = sum(1 for word in query_words if word in text) / max(len(query_words), 1)
            if score > 0:
                results.append((memory, score))
        
        return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
    
    def find_related_memories(self, memory_id: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Find memories semantically related to a given memory."""
        # Find the memory by ID
        target_memory = None
        target_embedding = None
        
        for memory, embedding in self.memory_store:
            if memory.get('id') == memory_id:
                target_memory = memory
                target_embedding = embedding
                break
        
        if target_memory is None or target_embedding is None:
            return []
        
        # Search using the memory's embedding
        query_text = self._memory_to_text(target_memory)
        return self.search(query_text, top_k=top_k + 1, min_score=0.5)
    
    def reindex_all(self, memories: List[Dict]):
        """Rebuild entire index from scratch."""
        print(f"[SEMANTIC] Reindexing {len(memories)} memories...")
        
        # Clear existing
        self.index = None
        self.memory_store = []
        
        # Add all memories
        for memory in memories:
            self.add_memory(memory)
        
        # Save
        self._save_index()
        print(f"[SEMANTIC] Reindexing complete")
    
    def shutdown(self):
        """Save index before shutdown."""
        self._save_index()


# =======================
# GLOBAL INSTANCE
# =======================
_retrieval = None

def get_retrieval() -> SemanticRetrieval:
    """Get or create semantic retrieval instance."""
    global _retrieval
    if _retrieval is None:
        _retrieval = SemanticRetrieval()
    return _retrieval

def semantic_search(query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
    """Perform semantic search."""
    return get_retrieval().search(query, top_k)

def add_to_index(memory: Dict):
    """Add memory to semantic index."""
    get_retrieval().add_memory(memory)

def find_related(memory_id: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
    """Find related memories."""
    return get_retrieval().find_related_memories(memory_id, top_k)

def shutdown_semantic():
    """Shutdown and save."""
    if _retrieval:
        _retrieval.shutdown()
