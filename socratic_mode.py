from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import re
import os
import random

class SocraticSession:
    """
    A guided thinking session using Socratic method.
    """
    def __init__(self, problem_statement):
        self.problem = problem_statement
        self.questions_asked = []
        self.insights_reached = []
        self.stage = "clarification"  # clarification → exploration → solution
        self.started_at = datetime.now()

class SocraticEngine:
    """
    Guides user through problem-solving using questions.
    """
    
    def should_enter_socratic_mode(self, message: str, context: Dict) -> bool:
        """
        Decide if Socratic mode is appropriate.
        
        Enter when:
        - User presents a dilemma ("should I do X or Y?")
        - User asks for advice on decision
        - User seems stuck on a problem
        
        Don't enter when:
        - User needs factual info
        - User is in crisis (needs support, not questions)
        - User asks simple question
        """
        
        # Dilemma detection
        dilemma_patterns = [
            r"should i (.+) or (.+)",
            r"not sure if i should (.+)",
            r"can't decide (.+)",
            r"what do you think i should (.+)"
        ]
        
        for pattern in dilemma_patterns:
            if re.search(pattern, message.lower()):
                # Check emotional state - don't use Socratic if distressed
                if context.get('emotion') in ['anxiety', 'panic', 'sadness']:
                    return False  # Needs support, not questions
                
                return True
        
        return False
    
    def generate_clarifying_questions(self, problem: str) -> List[str]:
        """
        Generate questions to clarify the problem.
        
        Clarification questions help user define the problem better.
        """
        questions = []
        
        # What exactly is the problem?
        questions.append("Help me understand - what exactly is making this tough for you?")
        
        # What's at stake?
        questions.append("What happens if you make the wrong choice here?")
        
        # What do you already know?
        questions.append("What've you already tried or considered?")
        
        return questions
    
    def generate_exploration_questions(self, problem: str, context: Dict) -> List[str]:
        """
        Generate questions to explore the problem deeper.
        
        Exploration questions help user think through implications.
        """
        questions = []
        
        # Future consequences
        questions.append("If you went with option A, where do you reckon you'd be in 6 months?")
        
        # Values alignment
        questions.append("Which choice feels more like *you*, you know what I mean?")
        
        # Fear analysis
        questions.append("What's the worst that could happen if you're wrong?")
        
        # Opportunity analysis
        questions.append("And the best that could happen if you're right?")
        
        return questions
    
    def generate_solution_questions(self, problem: str, insights: List[str]) -> List[str]:
        """
        Generate questions to guide toward solution.
        
        Solution questions help user commit to action.
        """
        questions = []
        
        # Decision clarity
        questions.append("So based on all that - what's your gut telling you?")
        
        # Commitment
        questions.append("If you were to make a choice right now, what would it be?")
        
        # Action planning
        questions.append("What's the first small step you could take?")
        
        return questions
    
    def format_socratic_response(self, session: SocraticSession, user_answer: str) -> str:
        """
        Generate next Socratic question based on where we are.
        """
        
        if session.stage == "clarification":
            questions = self.generate_clarifying_questions(session.problem)
            
            # After 2 clarification questions, move to exploration
            if len(session.questions_asked) >= 2:
                session.stage = "exploration"
            
            return random.choice(questions)
        
        elif session.stage == "exploration":
            questions = self.generate_exploration_questions(session.problem, {})
            
            # After 3 exploration questions, move to solution
            if len(session.questions_asked) >= 5:
                session.stage = "solution"
            
            return random.choice(questions)
        
        elif session.stage == "solution":
            questions = self.generate_solution_questions(session.problem, [])
            
            return random.choice(questions)
        
        return "What're you thinking now?"
    
    def get_socratic_instruction(self) -> str:
        """Get system prompt instruction for Socratic mode."""
        return """
**SOCRATIC MODE ACTIVE:**
Instead of giving direct advice, guide the user to their own answer through strategic questions.
Ask 1-2 questions that help them think deeper about their problem.
Be gentle, not interrogative. Use your Cockney warmth.
Focus on helping them discover the answer themselves.
"""

# =======================
# GLOBAL INSTANCE
# =======================
_socratic_engine = None
_current_session = None

def init_socratic_mode():
    """Initialize Socratic mode system."""
    global _socratic_engine
    _socratic_engine = SocraticEngine()
    print("[SOCRATIC] ✓ Socratic mode initialized")

def should_enter_socratic_mode(message: str, context: Dict) -> bool:
    """Check if Socratic mode should be activated."""
    if _socratic_engine:
        return _socratic_engine.should_enter_socratic_mode(message, context)
    return False

def get_socratic_instruction() -> str:
    """Get system prompt instruction."""
    if _socratic_engine:
        return _socratic_engine.get_socratic_instruction()
    return ""

def start_session(problem_statement: str) -> SocraticSession:
    """Start a new Socratic session."""
    global _current_session
    _current_session = SocraticSession(problem_statement)
    return _current_session

def get_current_session() -> Optional[SocraticSession]:
    """Get current session."""
    return _current_session

def end_session():
    """End current session."""
    global _current_session
    _current_session = None