# memory_management/retrieval.py
"""
Memory retrieval pipeline: search → score → return.
Always-on background knowledge for AiD.
"""

from datetime import datetime
from typing import List, Dict, Optional
from .memory_vector_store import get_memory_store
from .scoring import score_memories

class MemoryRetrieval:
    """
    Handles memory retrieval with intelligent scoring.
    Always retrieves memories on every user message (no triggers).
    """
    
    def __init__(self):
        self.memory_store = get_memory_store()
        print("[MEMORY RETRIEVAL] Initialized")
    
    def retrieve(self, query: str, top_k: int = 15, min_score: float = 0.05) -> List[Dict]:
        """
        Retrieve relevant memories for a query.
        
        Pipeline:
        1. FAISS semantic search (top 50 candidates)
        2. Score each candidate (semantic × temporal × access × entity × importance)
        3. Sort by final score
        4. Deduplicate very similar memories
        5. Return top_k memories
        
        Args:
            query: User's message/query
            top_k: Number of memories to return (15-20 recommended)
            min_score: Minimum score threshold (filter out irrelevant)
        
        Returns:
            List of memory dicts with scores and metadata
        """
        # Step 1: Semantic search
        search_results = self.memory_store.search(query, top_k=50)
        
        if not search_results:
            return []
        
        # Step 2: Score all candidates
        scored_memories = score_memories(search_results, query)
        
        # Step 3: Filter by minimum score
        scored_memories = [(mem, score, comp) for mem, score, comp in scored_memories if score >= min_score]
        
        # Step 4: Deduplicate (remove very similar memories)
        deduplicated = self._deduplicate_memories(scored_memories)
        
        # Step 5: Take top_k
        top_memories = deduplicated[:top_k]
        
        # Step 6: Update access stats for top 5 (these will likely be used)
        for memory, score, components in top_memories[:5]:
            self.memory_store.update_access_stats(memory["id"])
        
        # Format for return (include score and components for debugging)
        results = []
        for memory, score, components in top_memories:
            result = memory.copy()
            result["retrieval_score"] = score
            result["score_components"] = components
            results.append(result)
        
        return results
    
    def _deduplicate_memories(self, scored_memories: List) -> List:
        """
        Remove near-duplicate memories (>95% similar content).
        Keeps the higher-scoring version.
        """
        if len(scored_memories) <= 1:
            return scored_memories
        
        deduplicated = []
        seen_contents = set()
        
        for memory, score, components in scored_memories:
            content = memory["content"].lower().strip()
            
            # Check if very similar to any seen content
            is_duplicate = False
            for seen in seen_contents:
                similarity = self._string_similarity(content, seen)
                if similarity > 0.95:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append((memory, score, components))
                seen_contents.add(content)
        
        return deduplicated
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """
        Quick string similarity check (Jaccard similarity on words).
        """
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def format_for_context(self, memories: List[Dict]) -> str:
        """
        Format retrieved memories for injection into AiD's context.
        
        Returns formatted string ready for prompt inclusion.
        """
        if not memories:
            return ""
        
        lines = ["[RELEVANT MEMORIES]"]
        lines.append("You have access to these memories from past conversations:")
        
        for memory in memories:
            # Format memory with metadata
            score = memory.get("retrieval_score", 0.0)
            
            # Calculate age
            try:
                timestamp = datetime.fromisoformat(memory["timestamp"])
                age = self._format_age(datetime.now() - timestamp)
            except:
                age = "unknown"
            
            access_count = memory.get("access_count", 1)
            
            # Format line
            line = f"• [Score: {score:.2f}, Age: {age}, Used: {access_count}×] {memory['content']}"
            lines.append(line)
        
        lines.append("")
        lines.append("Use relevant memories naturally. Don't announce \"I remember\" - just incorporate information.")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_age(self, timedelta) -> str:
        """Format timedelta as human-readable age"""
        days = timedelta.total_seconds() / 86400
        
        if days < 1:
            hours = timedelta.total_seconds() / 3600
            return f"{int(hours)}h"
        elif days < 7:
            return f"{int(days)}d"
        elif days < 30:
            weeks = days / 7
            return f"{int(weeks)}w"
        elif days < 365:
            months = days / 30
            return f"{int(months)}mo"
        else:
            years = days / 365
            return f"{years:.1f}y"
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about memory system"""
        return self.memory_store.get_stats()

# Global instance
_retrieval_system = None

def get_retrieval_system():
    """Get or create global retrieval system instance"""
    global _retrieval_system
    if _retrieval_system is None:
        _retrieval_system = MemoryRetrieval()
    return _retrieval_system

def retrieve_memories(query: str, top_k: int = 15):
    """Convenience function for retrieving memories"""
    retrieval = get_retrieval_system()
    return retrieval.retrieve(query, top_k)

def format_memories_for_context(memories: List[Dict]) -> str:
    """Convenience function for formatting memories"""
    retrieval = get_retrieval_system()
    return retrieval.format_for_context(memories)