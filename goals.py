"""
Goals Tracking System - Phase 4
Track user goals, milestones, and progress
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import uuid


class GoalTracker:
    """
    Comprehensive goal tracking system.
    """
    
    def __init__(self, data_dir: str = "Persona/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.goals_file = self.data_dir / "goals.json"
        self.goals = {}
        self.load_goals()
    
    def create_goal(self, title: str, description: str = "", 
                   deadline: Optional[datetime] = None,
                   category: str = "personal",
                   milestones: Optional[List[str]] = None) -> str:
        """Create a new goal."""
        goal_id = str(uuid.uuid4())
        
        goal = {
            'id': goal_id,
            'title': title,
            'description': description,
            'category': category,
            'status': 'active',
            'created': datetime.now().isoformat(),
            'deadline': deadline.isoformat() if deadline else None,
            'milestones': milestones or [],
            'completed_milestones': [],
            'progress_updates': [],
            'completion_percentage': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        self.goals[goal_id] = goal
        self.save_goals()
        
        print(f"[GOALS] Created new goal: {title}")
        return goal_id
    
    def update_progress(self, goal_id: str, update: str, 
                       progress_percentage: Optional[int] = None):
        """Add progress update to goal."""
        if goal_id not in self.goals:
            print(f"[GOALS] Goal not found: {goal_id}")
            return
        
        progress_entry = {
            'timestamp': datetime.now().isoformat(),
            'update': update
        }
        
        if progress_percentage is not None:
            progress_entry['progress'] = progress_percentage
            self.goals[goal_id]['completion_percentage'] = progress_percentage
        
        self.goals[goal_id]['progress_updates'].append(progress_entry)
        self.goals[goal_id]['last_updated'] = datetime.now().isoformat()
        
        # Auto-complete if 100%
        if progress_percentage == 100:
            self.complete_goal(goal_id)
        
        self.save_goals()
        print(f"[GOALS] Updated progress for: {self.goals[goal_id]['title']}")
    
    def complete_milestone(self, goal_id: str, milestone: str):
        """Mark a milestone as completed."""
        if goal_id not in self.goals:
            return
        
        goal = self.goals[goal_id]
        
        if milestone in goal['milestones'] and milestone not in goal['completed_milestones']:
            goal['completed_milestones'].append(milestone)
            goal['last_updated'] = datetime.now().isoformat()
            
            # Update progress percentage based on milestones
            total_milestones = len(goal['milestones'])
            completed_milestones = len(goal['completed_milestones'])
            goal['completion_percentage'] = int((completed_milestones / total_milestones) * 100)
            
            # Add progress update
            goal['progress_updates'].append({
                'timestamp': datetime.now().isoformat(),
                'update': f"Completed milestone: {milestone}"
            })
            
            self.save_goals()
            print(f"[GOALS] Milestone completed: {milestone}")
            
            # Check if all milestones done
            if completed_milestones == total_milestones:
                self.complete_goal(goal_id)
    
    def complete_goal(self, goal_id: str):
        """Mark goal as completed."""
        if goal_id not in self.goals:
            return
        
        goal = self.goals[goal_id]
        goal['status'] = 'completed'
        goal['completed_date'] = datetime.now().isoformat()
        goal['completion_percentage'] = 100
        goal['last_updated'] = datetime.now().isoformat()
        
        self.save_goals()
        print(f"[GOALS] 🎉 Goal completed: {goal['title']}")
    
    def pause_goal(self, goal_id: str, reason: str = ""):
        """Pause a goal."""
        if goal_id not in self.goals:
            return
        
        self.goals[goal_id]['status'] = 'paused'
        self.goals[goal_id]['pause_reason'] = reason
        self.goals[goal_id]['paused_date'] = datetime.now().isoformat()
        self.save_goals()
        
        print(f"[GOALS] Goal paused: {self.goals[goal_id]['title']}")
    
    def resume_goal(self, goal_id: str):
        """Resume a paused goal."""
        if goal_id not in self.goals:
            return
        
        if self.goals[goal_id]['status'] == 'paused':
            self.goals[goal_id]['status'] = 'active'
            self.goals[goal_id]['resumed_date'] = datetime.now().isoformat()
            self.save_goals()
            
            print(f"[GOALS] Goal resumed: {self.goals[goal_id]['title']}")
    
    def abandon_goal(self, goal_id: str, reason: str = ""):
        """Mark goal as abandoned."""
        if goal_id not in self.goals:
            return
        
        self.goals[goal_id]['status'] = 'abandoned'
        self.goals[goal_id]['abandon_reason'] = reason
        self.goals[goal_id]['abandoned_date'] = datetime.now().isoformat()
        self.save_goals()
        
        print(f"[GOALS] Goal abandoned: {self.goals[goal_id]['title']}")
    
    def get_active_goals(self) -> List[Dict]:
        """Get all active goals."""
        return [g for g in self.goals.values() if g['status'] == 'active']
    
    def get_all_goals(self, status: Optional[str] = None) -> List[Dict]:
        """Get all goals, optionally filtered by status."""
        if status:
            return [g for g in self.goals.values() if g['status'] == status]
        return list(self.goals.values())
    
    def get_goal(self, goal_id: str) -> Optional[Dict]:
        """Get specific goal."""
        return self.goals.get(goal_id)
    
    def get_goals_by_category(self, category: str) -> List[Dict]:
        """Get goals in a category."""
        return [g for g in self.goals.values() if g['category'] == category]
    
    def get_overdue_goals(self) -> List[Dict]:
        """Get goals past their deadline."""
        now = datetime.now()
        overdue = []
        
        for goal in self.goals.values():
            if goal['status'] == 'active' and goal['deadline']:
                deadline = datetime.fromisoformat(goal['deadline'])
                if deadline < now:
                    overdue.append(goal)
        
        return overdue
    
    def get_upcoming_deadlines(self, days: int = 7) -> List[Dict]:
        """Get goals with deadlines in next N days."""
        now = datetime.now()
        future_cutoff = now + timedelta(days=days)
        
        upcoming = []
        for goal in self.goals.values():
            if goal['status'] == 'active' and goal['deadline']:
                deadline = datetime.fromisoformat(goal['deadline'])
                if now < deadline <= future_cutoff:
                    upcoming.append(goal)
        
        return sorted(upcoming, key=lambda g: g['deadline'])
    
    def get_summary(self, goal_id: str) -> str:
        """Get text summary of a goal."""
        if goal_id not in self.goals:
            return "Goal not found"
        
        goal = self.goals[goal_id]
        summary = f"**{goal['title']}**\n"
        summary += f"Status: {goal['status']}\n"
        
        if goal['description']:
            summary += f"Description: {goal['description']}\n"
        
        if goal['deadline']:
            deadline = datetime.fromisoformat(goal['deadline'])
            days_left = (deadline - datetime.now()).days
            summary += f"Deadline: {deadline.strftime('%Y-%m-%d')} ({days_left} days)\n"
        
        summary += f"Progress: {goal['completion_percentage']}%\n"
        
        if goal['milestones']:
            completed = len(goal['completed_milestones'])
            total = len(goal['milestones'])
            summary += f"Milestones: {completed}/{total} completed\n"
        
        if goal['progress_updates']:
            latest = goal['progress_updates'][-1]
            summary += f"\nLatest update: {latest['update']}\n"
        
        return summary
    
    def get_all_summaries(self, active_only: bool = True) -> str:
        """Get summaries of all goals."""
        goals = self.get_active_goals() if active_only else list(self.goals.values())
        
        if not goals:
            return "No goals tracked"
        
        summaries = []
        for goal in goals:
            summaries.append(self.get_summary(goal['id']))
        
        return "\n\n".join(summaries)
    
    def get_statistics(self) -> Dict:
        """Get statistics about goals."""
        stats = {
            'total': len(self.goals),
            'active': len([g for g in self.goals.values() if g['status'] == 'active']),
            'completed': len([g for g in self.goals.values() if g['status'] == 'completed']),
            'paused': len([g for g in self.goals.values() if g['status'] == 'paused']),
            'abandoned': len([g for g in self.goals.values() if g['status'] == 'abandoned']),
            'overdue': len(self.get_overdue_goals()),
            'upcoming_deadlines': len(self.get_upcoming_deadlines(7))
        }
        
        # Calculate average completion percentage for active goals
        active_goals = self.get_active_goals()
        if active_goals:
            avg_completion = sum(g['completion_percentage'] for g in active_goals) / len(active_goals)
            stats['average_progress'] = round(avg_completion, 1)
        
        return stats
    
    def save_goals(self):
        """Save goals to disk."""
        with open(self.goals_file, 'w', encoding='utf-8') as f:
            json.dump(self.goals, f, indent=2, ensure_ascii=False)
    
    def load_goals(self):
        """Load goals from disk."""
        if self.goals_file.exists():
            try:
                with open(self.goals_file, 'r', encoding='utf-8') as f:
                    self.goals = json.load(f)
                print(f"[GOALS] Loaded {len(self.goals)} goals")
            except Exception as e:
                print(f"[GOALS] Error loading goals: {e}")
                self.goals = {}


# =======================
# GLOBAL INSTANCE
# =======================
_tracker = None

def get_tracker() -> GoalTracker:
    """Get or create goal tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = GoalTracker()
    return _tracker

def init_goal_tracker():
    """Initialize goal tracker."""
    get_tracker()
    print("[GOALS] Goal tracker initialized")

def create_goal(title: str, **kwargs) -> str:
    """Create a new goal."""
    return get_tracker().create_goal(title, **kwargs)

def update_goal_progress(goal_id: str, update: str, progress: Optional[int] = None):
    """Update goal progress."""
    get_tracker().update_progress(goal_id, update, progress)

def complete_milestone(goal_id: str, milestone: str):
    """Complete a milestone."""
    get_tracker().complete_milestone(goal_id, milestone)

def get_active_goals() -> List[Dict]:
    """Get active goals."""
    return get_tracker().get_active_goals()

def get_goal_summary(goal_id: str) -> str:
    """Get goal summary."""
    return get_tracker().get_summary(goal_id)

def get_all_summaries(active_only: bool = True) -> str:
    """Get all goal summaries."""
    return get_tracker().get_all_summaries(active_only)

def get_overdue_goals() -> List[Dict]:
    """Get overdue goals."""
    return get_tracker().get_overdue_goals()

def get_upcoming_deadlines(days: int = 7) -> List[Dict]:
    """Get upcoming deadlines."""
    return get_tracker().get_upcoming_deadlines(days)

def get_goal_stats() -> Dict:
    """Get goal statistics."""
    return get_tracker().get_statistics()
