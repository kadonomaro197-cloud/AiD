# memory_management/scoring.py
"""
Scoring functions for memory retrieval.
Combines semantic similarity with temporal, access, entity, and importance factors.
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple
import math

def temporal_decay(memory_timestamp_str: str, current_time: datetime = None) -> float:
    """
    Calculate temporal decay factor for a memory.
    Recent memories score higher, old memories decay but never to zero.
    
    Decay curve:
    - 0-7 days: 1.0 (no decay)
    - 7-30 days: 1.0 → 0.7 (gentle decay)
    - 30-90 days: 0.7 → 0.4 (moderate decay)
    - 90-365 days: 0.4 → 0.2 (significant decay)
    - 365+ days: 0.2 → 0.05 (floor at 5% to keep searchable)
    
    Args:
        memory_timestamp_str: ISO format timestamp string
        current_time: Current time (defaults to now)
    
    Returns:
        Decay multiplier (0.05 - 1.0)
    """
    if current_time is None:
        current_time = datetime.now()
    
    try:
        memory_time = datetime.fromisoformat(memory_timestamp_str)
        age_seconds = (current_time - memory_time).total_seconds()
        age_days = age_seconds / 86400
    except:
        # If timestamp parsing fails, assume recent
        return 1.0
    
    # Apply decay curve
    if age_days <= 7:
        return 1.0
    elif age_days <= 30:
        # Linear decay from 1.0 to 0.7 over 23 days
        return 1.0 - (age_days - 7) * 0.013
    elif age_days <= 90:
        # Linear decay from 0.7 to 0.4 over 60 days
        return 0.7 - (age_days - 30) * 0.005
    elif age_days <= 365:
        # Linear decay from 0.4 to 0.2 over 275 days
        return 0.4 - (age_days - 90) * 0.00073
    else:
        # Logarithmic decay from 0.2 towards floor of 0.05
        years = age_days / 365
        return max(0.05, 0.2 * math.exp(-0.3 * (years - 1)))


def access_weight(access_count: int, last_accessed_str: str, current_time: datetime = None) -> float:
    """
    Calculate access pattern weight.
    Frequently-accessed memories score higher, but recent access matters too.
    
    Formula: access_boost × recency_boost
    - access_boost: 1.0 + log10(access_count) / 2  (caps at ~1.5 for 100 accesses)
    - recency_boost: 1.0 if accessed recently, decays if not accessed in 90+ days
    
    Args:
        access_count: Number of times memory has been retrieved
        last_accessed_str: ISO format timestamp of last access
        current_time: Current time (defaults to now)
    
    Returns:
        Access weight multiplier (0.7 - 1.5)
    """
    if current_time is None:
        current_time = datetime.now()
    
    # Access count boost (logarithmic to prevent runaway)
    access_boost = 1.0 + math.log10(max(1, access_count)) / 2
    access_boost = min(access_boost, 1.5)  # Cap at 1.5x
    
    # Recency boost (penalize memories not accessed in 90+ days)
    try:
        last_access = datetime.fromisoformat(last_accessed_str)
        days_since_access = (current_time - last_access).total_seconds() / 86400
        
        if days_since_access <= 90:
            recency_boost = 1.0  # Recently used, no penalty
        else:
            # Decay from 1.0 to 0.7 over next 275 days
            recency_boost = max(0.7, 1.0 - (days_since_access - 90) * 0.0011)
    except:
        recency_boost = 1.0
    
    return access_boost * recency_boost


def extract_entities(text: str) -> List[str]:
    """
    Extract entities (proper nouns, capitalized phrases) from text.
    Simple pattern-based extraction.
    
    Patterns:
    - Consecutive capitalized words (ESR Dominance, Capitol 01)
    - Single capitalized words followed by lowercase (Python, Discord)
    - Words with numbers (Project-17, RTX-3090)
    
    Args:
        text: Input text
    
    Returns:
        List of extracted entities
    """
    entities = []
    
    # Pattern 1: Consecutive capitalized words (2+ words)
    # Example: "ESR Dominance", "Adaptive Intelligence Daemon"
    pattern1 = r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)+\b'
    entities.extend(re.findall(pattern1, text))
    
    # Pattern 2: Single capitalized word (likely proper noun)
    # Example: "Python", "Discord", "Stellar"
    pattern2 = r'\b[A-Z][a-z]{2,}\b'
    entities.extend(re.findall(pattern2, text))
    
    # Pattern 3: Alphanumeric combinations (project names, model numbers)
    # Example: "RTX-3090", "GPT-4", "Qwen2.5"
    pattern3 = r'\b[A-Z][A-Za-z0-9\-\.]+\d+[A-Za-z0-9\-\.]*\b'
    entities.extend(re.findall(pattern3, text))
    
    # Pattern 4: ALL CAPS words (acronyms)
    # Example: "ESR", "RAG", "FAISS"
    pattern4 = r'\b[A-Z]{2,}\b'
    entities.extend(re.findall(pattern4, text))
    
    # Deduplicate and filter
    entities = list(set(entities))
    
    # Filter out common words that shouldn't be entities
    stopwords = {'The', 'This', 'That', 'These', 'Those', 'Here', 'There', 
                 'When', 'Where', 'What', 'Which', 'Who', 'How', 'Why'}
    entities = [e for e in entities if e not in stopwords]
    
    return entities


def entity_boost(query: str, memory_entities: List[str]) -> float:
    """
    Calculate entity matching boost.
    Precise matches for specific entities (ships, characters, locations).
    
    Args:
        query: User's search query
        memory_entities: List of entities in the memory
    
    Returns:
        Entity boost multiplier (1.0 - 1.5)
    """
    if not memory_entities:
        return 1.0
    
    # Extract entities from query
    query_entities = extract_entities(query)
    
    if not query_entities:
        return 1.0
    
    # Count exact matches
    matches = 0
    for qe in query_entities:
        for me in memory_entities:
            # Case-insensitive exact match
            if qe.lower() == me.lower():
                matches += 1
            # Partial match (query entity contained in memory entity)
            elif qe.lower() in me.lower() or me.lower() in qe.lower():
                matches += 0.5
    
    # Convert matches to boost factor
    if matches == 0:
        return 1.0
    elif matches < 1:
        return 1.1
    elif matches < 2:
        return 1.25
    else:
        return 1.5  # Cap at 1.5x for multiple matches


def compute_final_score(
    semantic_similarity: float,
    memory: Dict,
    query: str,
    current_time: datetime = None
) -> float:
    """
    Compute final retrieval score for a memory.
    
    Formula: semantic × temporal × access × entity × importance
    
    Args:
        semantic_similarity: FAISS similarity score (0-1)
        memory: Memory object with metadata
        query: User's search query
        current_time: Current time (defaults to now)
    
    Returns:
        Final score (0-5.0 theoretical max, typically 0-2.0)
    """
    # Get scoring components
    temporal = temporal_decay(memory["timestamp"], current_time)
    access = access_weight(memory["access_count"], memory["last_accessed"], current_time)
    entity = entity_boost(query, memory.get("entities", []))
    importance = memory.get("importance", 1.0)
    
    # Final multiplicative score
    final_score = (
        semantic_similarity * 
        temporal * 
        access * 
        entity * 
        importance
    )
    
    return final_score


def score_memories(
    search_results: List[Tuple[Dict, float]], 
    query: str,
    current_time: datetime = None
) -> List[Tuple[Dict, float, Dict]]:
    """
    Score a list of search results with full scoring breakdown.
    
    Args:
        search_results: List of (memory, semantic_similarity) tuples from FAISS
        query: User's search query
        current_time: Current time (defaults to now)
    
    Returns:
        List of (memory, final_score, components_dict) tuples, sorted by final_score
    """
    scored = []
    
    for memory, semantic_sim in search_results:
        # Compute all components
        temporal = temporal_decay(memory["timestamp"], current_time)
        access = access_weight(memory["access_count"], memory["last_accessed"], current_time)
        entity = entity_boost(query, memory.get("entities", []))
        importance = memory.get("importance", 1.0)
        
        # Final score
        final_score = semantic_sim * temporal * access * entity * importance
        
        # Component breakdown (for debugging)
        components = {
            "semantic": semantic_sim,
            "temporal": temporal,
            "access": access,
            "entity": entity,
            "importance": importance
        }
        
        scored.append((memory, final_score, components))
    
    # Sort by final score (descending)
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return scored