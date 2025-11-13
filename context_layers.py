from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import re
import os

class ContextLayer:
    """
    A layer of understanding about the user.
    
    Layers build on each other:
    - Layer 1: Facts ("User is a coder")
    - Layer 2: Patterns ("User codes best at night")
    - Layer 3: Meta ("User is transitioning careers into tech")
    - Layer 4: Narrative ("User is building confidence through projects")
    """
    
    def __init__(self, layer_level, content):
        self.layer_level = layer_level  # 1-4
        self.content = content
        self.supporting_evidence = []
        self.confidence = 0.5
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

class ContextManager:
    """
    Manages layered context about the user.
    """
    
    def __init__(self):
        self.layers = {
            1: [],  # Facts
            2: [],  # Patterns
            3: [],  # Meta-understanding
            4: []   # Narrative
        }
        self.load_layers()
    
    def add_evidence(self, message: str, interaction_context: Dict):
        """
        Add evidence that builds context layers.
        """
        
        # Layer 1: Extract facts
        facts = self._extract_facts(message)
        for fact in facts:
            self._add_to_layer(1, fact, message)
        
        # Layer 2: Detect patterns (requires multiple observations)
        if len(self.layers[1]) >= 5:
            patterns = self._detect_patterns()
            for pattern in patterns:
                self._add_to_layer(2, pattern, message)
        
        # Layer 3: Build meta-understanding (requires patterns)
        if len(self.layers[2]) >= 3:
            meta = self._build_meta_understanding()
            for understanding in meta:
                self._add_to_layer(3, understanding, message)
        
        # Layer 4: Construct narrative (requires meta-understanding)
        if len(self.layers[3]) >= 2:
            narrative = self._construct_narrative()
            if narrative:
                self._add_to_layer(4, narrative, message)
    
    def _add_to_layer(self, layer_level: int, content: str, evidence: str):
        """Add item to a layer."""
        # Check if content already exists
        for item in self.layers[layer_level]:
            if item.content == content:
                # Update existing
                item.last_updated = datetime.now()
                item.supporting_evidence.append(evidence)
                return
        
        # Add new
        new_layer = ContextLayer(layer_level, content)
        new_layer.supporting_evidence.append(evidence)
        self.layers[layer_level].append(new_layer)
    
    def _extract_facts(self, message: str) -> List[str]:
        """
        Extract factual statements.
        
        "I work as a teacher" → Fact: "User is a teacher"
        "I have 2 cats" → Fact: "User has 2 cats"
        """
        facts = []
        
        # Job/career
        job_patterns = [
            r"i work as (?:a|an) (.+)",
            r"i'm (?:a|an) (.+)",
            r"my job is (.+)"
        ]
        
        for pattern in job_patterns:
            match = re.search(pattern, message.lower())
            if match:
                facts.append(f"works as {match.group(1)}")
        
        # Family/pets
        if "cat" in message.lower():
            facts.append("has cat(s)")
        if "dog" in message.lower():
            facts.append("has dog(s)")
        
        return facts
    
    def _detect_patterns(self) -> List[str]:
        """
        Detect patterns from facts.
        
        Multiple mentions of coding at night → "codes at night"
        Multiple project mentions → "working on projects"
        """
        patterns = []
        
        # Count fact frequencies
        fact_counts = {}
        for fact in self.layers[1]:
            fact_content = fact.content
            fact_counts[fact_content] = fact_counts.get(fact_content, 0) + 1
        
        # Patterns = facts mentioned 3+ times
        for fact, count in fact_counts.items():
            if count >= 3:
                patterns.append(f"consistently {fact}")
        
        return patterns
    
    def _build_meta_understanding(self) -> List[str]:
        """
        Build higher-level understanding from patterns.
        
        "consistently codes" + "consistently learns new tech" + "mentions career change"
        → "transitioning into tech career"
        """
        meta = []
        
        # Look for career transition signals
        career_signals = [p for p in self.layers[2] if "learning" in p.content or "coding" in p.content]
        if len(career_signals) >= 2:
            meta.append("likely transitioning career into tech")
        
        # Look for hobby vs. profession signals
        # ... etc
        
        return meta
    
    def _construct_narrative(self) -> Optional[str]:
        """
        Construct the overarching narrative.
        
        This is the "story" of your relationship/journey.
        
        "User started learning to code 3 weeks ago, initially struggled but is now
        building confidence through hands-on projects. Seems to be considering a career
        transition into tech."
        """
        
        # Combine meta-understandings into coherent narrative
        meta_items = [layer.content for layer in self.layers[3]]
        
        if len(meta_items) >= 2:
            narrative = " and ".join(meta_items)
            return narrative
        
        return None
    
    def get_context_for_prompt(self, depth: str = "medium") -> str:
        """
        Get context to add to system prompt.
        
        Depth:
        - shallow: Just facts
        - medium: Facts + patterns
        - deep: Everything including narrative
        """
        
        context = ""
        
        if depth in ["shallow", "medium", "deep"]:
            # Add facts
            if self.layers[1]:
                context += "\n**WHAT I KNOW ABOUT YOU:**\n"
                for fact in self.layers[1][:5]:  # Top 5 facts
                    context += f"- {fact.content}\n"
        
        if depth in ["medium", "deep"]:
            # Add patterns
            if self.layers[2]:
                context += "\n**PATTERNS I'VE NOTICED:**\n"
                for pattern in self.layers[2][:3]:
                    context += f"- {pattern.content}\n"
        
        if depth == "deep":
            # Add narrative
            if self.layers[4]:
                latest_narrative = self.layers[4][-1]
                context += f"\n**THE BIGGER PICTURE:**\n{latest_narrative.content}\n"
        
        return context
    
    def get_summary(self) -> Dict:
        """Get summary of context layers."""
        return {
            "layer_1_count": len(self.layers[1]),
            "layer_2_count": len(self.layers[2]),
            "layer_3_count": len(self.layers[3]),
            "has_narrative": len(self.layers[4]) > 0
        }
    
    def load_layers(self):
        """Load context layers from file."""
        try:
            filepath = "Persona/data/context_layers.json"
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    for level in [1, 2, 3, 4]:
                        for item_data in data.get(str(level), []):
                            layer = ContextLayer(level, item_data['content'])
                            layer.confidence = item_data.get('confidence', 0.5)
                            layer.created_at = datetime.fromisoformat(item_data['created_at'])
                            layer.last_updated = datetime.fromisoformat(item_data['last_updated'])
                            layer.supporting_evidence = item_data.get('supporting_evidence', [])
                            self.layers[level].append(layer)
        except Exception as e:
            print(f"[CONTEXT LAYERS] Error loading: {e}")
    
    def save_layers(self):
        """Save context layers to file."""
        try:
            os.makedirs("Persona/data", exist_ok=True)
            filepath = "Persona/data/context_layers.json"
            
            data = {}
            for level in [1, 2, 3, 4]:
                data[str(level)] = []
                for layer in self.layers[level]:
                    data[str(level)].append({
                        'content': layer.content,
                        'confidence': layer.confidence,
                        'created_at': layer.created_at.isoformat(),
                        'last_updated': layer.last_updated.isoformat(),
                        'supporting_evidence': layer.supporting_evidence[:5]  # Keep last 5
                    })
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[CONTEXT LAYERS] Error saving: {e}")

# =======================
# GLOBAL INSTANCE
# =======================
_context_manager = None

def init_context_layers():
    """Initialize context layering system."""
    global _context_manager
    _context_manager = ContextManager()
    print("[CONTEXT LAYERS] ✓ Context layering initialized")

def add_evidence(message: str, interaction_context: Dict):
    """Add evidence to context layers."""
    if _context_manager:
        _context_manager.add_evidence(message, interaction_context)
        _context_manager.save_layers()

def get_context_for_prompt(depth: str = "medium") -> str:
    """Get context for system prompt."""
    if _context_manager:
        return _context_manager.get_context_for_prompt(depth)
    return ""

def get_summary() -> Dict:
    """Get summary of context layers."""
    if _context_manager:
        return _context_manager.get_summary()
    return {"layer_1_count": 0, "layer_2_count": 0, "layer_3_count": 0, "has_narrative": False}