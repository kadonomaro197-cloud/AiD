"""
Journal System - Phase 4
Collaborative reflection and daily journaling
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class JournalSystem:
    """
    Manages collaborative journaling and reflection.
    """
    
    def __init__(self, data_dir: str = "Persona/data/journal"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_entry = None
        self.entries_by_date = {}
        self._load_all_entries()
    
    def create_entry(self, content: str = "", date: Optional[datetime] = None) -> Dict:
        """
        Create a new journal entry.
        
        Args:
            content: Initial content
            date: Date for entry (defaults to today)
        
        Returns:
            Entry dict
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        # Check if entry exists for this date
        if date_str in self.entries_by_date:
            print(f"[JOURNAL] Entry already exists for {date_str}")
            return self.entries_by_date[date_str]
        
        entry = {
            'date': date_str,
            'created_at': datetime.now().isoformat(),
            'content': content,
            'sections': {},
            'tags': [],
            'mood': None,
            'highlights': [],
            'challenges': [],
            'thoughts': [],
            'last_modified': datetime.now().isoformat()
        }
        
        self.entries_by_date[date_str] = entry
        self.current_entry = entry
        self._save_entry(entry)
        
        print(f"[JOURNAL] Created entry for {date_str}")
        return entry
    
    def get_today_entry(self) -> Dict:
        """Get or create today's entry."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today in self.entries_by_date:
            return self.entries_by_date[today]
        
        return self.create_entry()
    
    def add_to_entry(self, content: str, section: str = "general",
                    date: Optional[datetime] = None) -> Dict:
        """
        Add content to a journal entry.
        
        Args:
            content: Content to add
            section: Section to add to (general, highlights, challenges, etc.)
            date: Date of entry (defaults to today)
        
        Returns:
            Updated entry
        """
        if date is None:
            entry = self.get_today_entry()
        else:
            date_str = date.strftime('%Y-%m-%d')
            entry = self.entries_by_date.get(date_str)
            if not entry:
                entry = self.create_entry(date=date)
        
        # Add to appropriate section
        if section == "highlights":
            entry['highlights'].append({
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
        elif section == "challenges":
            entry['challenges'].append({
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
        elif section == "thoughts":
            entry['thoughts'].append({
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # General content
            if entry['content']:
                entry['content'] += f"\n\n{content}"
            else:
                entry['content'] = content
        
        entry['last_modified'] = datetime.now().isoformat()
        self._save_entry(entry)
        
        return entry
    
    def add_highlight(self, content: str) -> Dict:
        """Add a highlight to today's entry."""
        return self.add_to_entry(content, section="highlights")
    
    def add_challenge(self, content: str) -> Dict:
        """Add a challenge to today's entry."""
        return self.add_to_entry(content, section="challenges")
    
    def add_thought(self, content: str) -> Dict:
        """Add a thought to today's entry."""
        return self.add_to_entry(content, section="thoughts")
    
    def set_mood(self, mood: str, date: Optional[datetime] = None):
        """Set mood for an entry."""
        entry = self.get_today_entry() if date is None else self.entries_by_date.get(date.strftime('%Y-%m-%d'))
        
        if entry:
            entry['mood'] = mood
            entry['last_modified'] = datetime.now().isoformat()
            self._save_entry(entry)
    
    def add_tags(self, tags: List[str], date: Optional[datetime] = None):
        """Add tags to an entry."""
        entry = self.get_today_entry() if date is None else self.entries_by_date.get(date.strftime('%Y-%m-%d'))
        
        if entry:
            for tag in tags:
                if tag not in entry['tags']:
                    entry['tags'].append(tag)
            
            entry['last_modified'] = datetime.now().isoformat()
            self._save_entry(entry)
    
    def get_entry(self, date: datetime) -> Optional[Dict]:
        """Get entry for specific date."""
        date_str = date.strftime('%Y-%m-%d')
        return self.entries_by_date.get(date_str)
    
    def get_recent_entries(self, days: int = 7) -> List[Dict]:
        """Get entries from last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        entries = []
        for date_str, entry in self.entries_by_date.items():
            entry_date = datetime.strptime(date_str, '%Y-%m-%d')
            if entry_date >= cutoff:
                entries.append(entry)
        
        return sorted(entries, key=lambda e: e['date'], reverse=True)
    
    def search_entries(self, query: str) -> List[Dict]:
        """Search entries by content."""
        query_lower = query.lower()
        results = []
        
        for entry in self.entries_by_date.values():
            # Search in content
            if query_lower in entry['content'].lower():
                results.append(entry)
                continue
            
            # Search in highlights/challenges/thoughts
            for highlight in entry['highlights']:
                if query_lower in highlight['content'].lower():
                    results.append(entry)
                    break
        
        return sorted(results, key=lambda e: e['date'], reverse=True)
    
    def get_entries_by_tag(self, tag: str) -> List[Dict]:
        """Get all entries with a specific tag."""
        return [
            entry for entry in self.entries_by_date.values()
            if tag in entry['tags']
        ]
    
    def format_entry(self, entry: Dict) -> str:
        """Format entry as readable text."""
        lines = [f"📔 **Journal Entry - {entry['date']}**\n"]
        
        if entry['mood']:
            lines.append(f"**Mood:** {entry['mood']}\n")
        
        if entry['content']:
            lines.append(f"**Content:**\n{entry['content']}\n")
        
        if entry['highlights']:
            lines.append("**Highlights:**")
            for h in entry['highlights']:
                lines.append(f"  ✨ {h['content']}")
            lines.append("")
        
        if entry['challenges']:
            lines.append("**Challenges:**")
            for c in entry['challenges']:
                lines.append(f"  🚧 {c['content']}")
            lines.append("")
        
        if entry['thoughts']:
            lines.append("**Thoughts:**")
            for t in entry['thoughts']:
                lines.append(f"  💭 {t['content']}")
            lines.append("")
        
        if entry['tags']:
            lines.append(f"**Tags:** {', '.join(entry['tags'])}")
        
        return "\n".join(lines)
    
    def get_weekly_summary(self) -> str:
        """Generate weekly journal summary."""
        entries = self.get_recent_entries(days=7)
        
        if not entries:
            return "No journal entries this week."
        
        summary = ["📊 **Weekly Journal Summary**\n"]
        summary.append(f"**Entries:** {len(entries)} days\n")
        
        # Collect all highlights
        all_highlights = []
        all_challenges = []
        all_tags = set()
        
        for entry in entries:
            all_highlights.extend([h['content'] for h in entry['highlights']])
            all_challenges.extend([c['content'] for c in entry['challenges']])
            all_tags.update(entry['tags'])
        
        if all_highlights:
            summary.append("**Week's Highlights:**")
            for h in all_highlights[:5]:  # Top 5
                summary.append(f"  ✨ {h}")
            summary.append("")
        
        if all_challenges:
            summary.append("**Challenges Faced:**")
            for c in all_challenges[:3]:  # Top 3
                summary.append(f"  🚧 {c}")
            summary.append("")
        
        if all_tags:
            summary.append(f"**Topics:** {', '.join(sorted(all_tags))}")
        
        return "\n".join(summary)
    
    def _save_entry(self, entry: Dict):
        """Save entry to disk."""
        entry_file = self.data_dir / f"{entry['date']}.json"
        
        with open(entry_file, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
    
    def _load_all_entries(self):
        """Load all journal entries from disk."""
        if not self.data_dir.exists():
            return
        
        for entry_file in self.data_dir.glob("*.json"):
            try:
                with open(entry_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    self.entries_by_date[entry['date']] = entry
            except Exception as e:
                print(f"[JOURNAL] Error loading {entry_file}: {e}")
        
        print(f"[JOURNAL] Loaded {len(self.entries_by_date)} journal entries")


# =======================
# GLOBAL INSTANCE
# =======================
_journal = None

def get_journal() -> JournalSystem:
    """Get or create journal instance."""
    global _journal
    if _journal is None:
        _journal = JournalSystem()
    return _journal

def init_journal():
    """Initialize journal system."""
    get_journal()
    print("[JOURNAL] Journal system initialized")

def create_entry(content: str = "", date: Optional[datetime] = None) -> Dict:
    """Create journal entry."""
    return get_journal().create_entry(content, date)

def add_highlight(content: str) -> Dict:
    """Add highlight to today."""
    return get_journal().add_highlight(content)

def add_challenge(content: str) -> Dict:
    """Add challenge to today."""
    return get_journal().add_challenge(content)

def add_thought(content: str) -> Dict:
    """Add thought to today."""
    return get_journal().add_thought(content)

def get_today() -> Dict:
    """Get today's entry."""
    return get_journal().get_today_entry()

def get_weekly_summary() -> str:
    """Get weekly summary."""
    return get_journal().get_weekly_summary()
