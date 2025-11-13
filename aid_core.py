"""
AiD Core Integration - Complete System Coordinator
Brings together all Phase 2-5 systems into unified whole

This is the main integration file that coordinates all AiD subsystems.
"""

from datetime import datetime
import threading
from typing import Dict, Optional, List


class AiDCore:
    """
    Central coordinator for all AiD systems.
    Integrates: Memory, Persona, Goals, Mood, Activity, Proactive, Voice, etc.
    """
    
    def __init__(self):
        self.initialized = False
        self.systems = {}
        self.lock = threading.Lock()
    
    def initialize_all(self):
        """Initialize all AiD systems."""
        if self.initialized:
            return
        
        print("\n" + "="*60)
        print("INITIALIZING AiD COMPLETE SYSTEM")
        print("="*60)
        
        # ====================
        # PHASE 1: Core Memory (should already exist)
        # ====================
        print("\n[PHASE 1] Core Memory Systems...")
        try:
            import stm, ltm, pattern_tracker
            self.systems['stm'] = stm
            self.systems['ltm'] = ltm
            self.systems['pattern_tracker'] = pattern_tracker
            print("  ✓ STM, LTM, Pattern Tracker loaded")
        except ImportError as e:
            print(f"  ✗ Core memory import error: {e}")
        
        # ====================
        # PHASE 2: Memory Orchestration & Semantic
        # ====================
        print("\n[PHASE 2] Memory Orchestration...")
        try:
            import orchestrator
            orchestrator.get_orchestrator()  # Initialize
            self.systems['orchestrator'] = orchestrator
            print("  ✓ Memory Orchestrator initialized")
        except ImportError:
            print("  ✗ Orchestrator not found (install from files)")
        
        try:
            import semantic_retrieval
            semantic_retrieval.get_retrieval()  # Initialize
            self.systems['semantic'] = semantic_retrieval
            print("  ✓ Semantic Retrieval initialized")
        except ImportError:
            print("  ⚠ Semantic retrieval not available")
        
        try:
            import enhanced_formation
            enhanced_formation.get_formation()  # Initialize
            self.systems['formation'] = enhanced_formation
            print("  ✓ Enhanced Formation initialized")
        except ImportError:
            print("  ⚠ Enhanced formation not available")
        
        # ====================
        # PHASE 3: Persona Systems (should exist)
        # ====================
        print("\n[PHASE 3] Persona Systems...")
        try:
            import personality, relationship, preference_learning, routine_learning
            self.systems['personality'] = personality
            self.systems['relationship'] = relationship
            self.systems['preferences'] = preference_learning
            self.systems['routines'] = routine_learning
            print("  ✓ Personality systems loaded")
        except ImportError as e:
            print(f"  ⚠ Some persona systems missing: {e}")
        
        # ====================
        # PHASE 4: Advanced Features
        # ====================
        print("\n[PHASE 4] Advanced Features...")
        
        # Goals
        try:
            import goals
            goals.init_goal_tracker()
            self.systems['goals'] = goals
            print("  ✓ Goal Tracker initialized")
        except ImportError:
            print("  ⚠ Goals system not available")
        
        # Mood
        try:
            import mood
            mood.init_mood_tracker()
            self.systems['mood'] = mood
            print("  ✓ Mood Tracker initialized")
        except ImportError:
            print("  ⚠ Mood tracker not available")
        
        # Activity
        try:
            import activity_log
            activity_log.init_activity_logger()
            self.systems['activity'] = activity_log
            print("  ✓ Activity Logger initialized")
        except ImportError:
            print("  ⚠ Activity logger not available")
        
        # Proactive
        try:
            import proactive
            # Note: Proactive needs a send_callback, set up later
            self.systems['proactive'] = proactive
            print("  ✓ Proactive Engine loaded (awaiting callback)")
        except ImportError:
            print("  ⚠ Proactive engine not available")
        
        # Reminders
        try:
            import reminders
            # Reminders also need callback
            self.systems['reminders'] = reminders
            print("  ✓ Reminders loaded (awaiting callback)")
        except ImportError:
            print("  ⚠ Reminders not available")
        
        # Journal
        try:
            import journal
            journal.init_journal()
            self.systems['journal'] = journal
            print("  ✓ Journal initialized")
        except ImportError:
            print("  ⚠ Journal not available")
        
        # Avatar
        try:
            import avatar
            avatar.init_avatar()
            self.systems['avatar'] = avatar
            print("  ✓ Avatar initialized")
        except ImportError:
            print("  ⚠ Avatar not available")
        
        # ====================
        # PHASE 5: Voice & Advanced
        # ====================
        print("\n[PHASE 5] Voice & Advanced Features...")
        try:
            import voice_handler
            voice_handler.init_voice()
            self.systems['voice'] = voice_handler
            
            status = voice_handler.is_voice_available()
            if status['tts'] and status['stt']:
                print("  ✓ Voice (TTS + STT) initialized")
            elif status['tts']:
                print("  ✓ Voice (TTS only) initialized")
            elif status['stt']:
                print("  ✓ Voice (STT only) initialized")
            else:
                print("  ⚠ Voice not available (install dependencies)")
        except ImportError:
            print("  ⚠ Voice handler not available")
        
        print("\n" + "="*60)
        print(f"✓ AiD FULLY INITIALIZED - {len(self.systems)} systems active")
        print("="*60 + "\n")
        
        self.initialized = True
    
    def process_message(self, user_message: str, user: str = "User") -> Dict:
        """
        Process incoming message through all systems.
        Returns complete context for LLM.
        """
        if not self.initialized:
            self.initialize_all()
        
        with self.lock:
            context = {
                'message': user_message,
                'user': user,
                'timestamp': datetime.now().isoformat(),
                'memory_context': [],
                'personality_context': {},
                'goals_context': [],
                'mood_context': None,
                'relationship_context': None
            }
            
            # 1. Retrieve relevant memories (orchestrator)
            if 'orchestrator' in self.systems:
                try:
                    memories = self.systems['orchestrator'].retrieve_memory(
                        user_message, 
                        limit=5, 
                        mode="hybrid"
                    )
                    context['memory_context'] = memories
                except Exception as e:
                    print(f"[CORE] Memory retrieval error: {e}")
            
            # 2. Analyze for memory formation
            if 'formation' in self.systems:
                try:
                    analysis = self.systems['formation'].analyze_for_memory(
                        user_message, 
                        user
                    )
                    context['memory_analysis'] = analysis
                    
                    # Auto-create memory if important
                    if analysis['should_remember']:
                        memory = self.systems['formation'].get_formation().create_memory_from_analysis(analysis)
                        if memory and 'orchestrator' in self.systems:
                            self.systems['orchestrator'].add_memory(
                                content=memory['content'],
                                category=memory.get('categories', ['general'])[0],
                                importance=memory['importance'],
                                metadata={'tags': memory.get('tags', [])}
                            )
                except Exception as e:
                    print(f"[CORE] Formation error: {e}")
            
            # 3. Analyze mood
            if 'mood' in self.systems:
                try:
                    self.systems['mood'].analyze_message(user_message)
                    trend = self.systems['mood'].get_mood_trend(days=7)
                    context['mood_context'] = trend
                    
                    # Update avatar based on detected emotion
                    if 'avatar' in self.systems and trend.get('dominant_emotions'):
                        dominant = trend['dominant_emotions'][0]
                        self.systems['avatar'].set_from_emotion(dominant)
                except Exception as e:
                    print(f"[CORE] Mood error: {e}")
            
            # 4. Log activity
            if 'activity' in self.systems:
                try:
                    self.systems['activity'].log_message(user_message, user)
                except Exception as e:
                    print(f"[CORE] Activity logging error: {e}")
            
            # 5. Check goals
            if 'goals' in self.systems:
                try:
                    active_goals = self.systems['goals'].get_active_goals()
                    context['goals_context'] = active_goals[:3]  # Top 3
                except Exception as e:
                    print(f"[CORE] Goals error: {e}")
            
            # 6. Get relationship context
            if 'relationship' in self.systems:
                try:
                    rel_status = self.systems['relationship'].get_relationship_status()
                    context['relationship_context'] = rel_status
                except Exception as e:
                    print(f"[CORE] Relationship error: {e}")
            
            # 7. Update proactive system
            if 'proactive' in self.systems:
                try:
                    self.systems['proactive'].record_interaction()
                except Exception as e:
                    print(f"[CORE] Proactive error: {e}")
            
            return context
    
    def post_response_processing(self, user_msg: str, aid_response: str):
        """
        Process after AiD responds - update systems.
        """
        # 1. Analyze AiD's response for mood/emotion
        if 'mood' in self.systems:
            try:
                self.systems['mood'].analyze_message(aid_response)
            except:
                pass
        
        # 2. Log activity
        if 'activity' in self.systems:
            try:
                self.systems['activity'].log_message(
                    user_msg, 
                    "User",
                    aid_response
                )
            except:
                pass
        
        # 3. Check if should add to journal
        if 'journal' in self.systems and 'formation' in self.systems:
            try:
                analysis = self.systems['formation'].analyze_for_memory(user_msg, "User")
                if analysis['importance_score'] >= 0.7:
                    # Significant conversation - add to journal
                    self.systems['journal'].add_thought(
                        f"Discussion: {user_msg[:100]}... | Response: {aid_response[:100]}..."
                    )
            except:
                pass
    
    def start_proactive_systems(self, send_callback):
        """
        Start systems that need callbacks (proactive, reminders).
        
        Args:
            send_callback: Function(message_str) to send messages to user
        """
        if 'proactive' in self.systems:
            try:
                self.systems['proactive'].init_proactive(send_callback)
                print("[CORE] Proactive engagement started")
            except Exception as e:
                print(f"[CORE] Proactive start error: {e}")
        
        if 'reminders' in self.systems:
            try:
                def reminder_callback(message, reminder_data):
                    send_callback(f"⏰ Reminder: {message}")
                
                self.systems['reminders'].init_reminders(reminder_callback)
                print("[CORE] Reminders started")
            except Exception as e:
                print(f"[CORE] Reminders start error: {e}")
    
    def shutdown(self):
        """Gracefully shutdown all systems."""
        print("\n[SHUTDOWN] Saving all data...")
        
        # Stop proactive systems
        if 'proactive' in self.systems:
            try:
                self.systems['proactive'].get_proactive().stop()
            except:
                pass
        
        if 'reminders' in self.systems:
            try:
                self.systems['reminders'].get_reminder_manager().stop()
            except:
                pass
        
        # Save all data
        if 'orchestrator' in self.systems:
            try:
                self.systems['orchestrator'].get_orchestrator().auto_maintain()
            except:
                pass
        
        if 'semantic' in self.systems:
            try:
                self.systems['semantic'].shutdown_semantic()
            except:
                pass
        
        print("[SHUTDOWN] All systems saved and stopped")
    
    def get_system_status(self) -> Dict:
        """Get status of all systems."""
        status = {
            'initialized': self.initialized,
            'active_systems': list(self.systems.keys()),
            'system_count': len(self.systems)
        }
        
        # Get orchestrator status if available
        if 'orchestrator' in self.systems:
            try:
                status['memory_status'] = self.systems['orchestrator'].get_status()
            except:
                pass
        
        # Get goals stats
        if 'goals' in self.systems:
            try:
                status['goals_stats'] = self.systems['goals'].get_goal_stats()
            except:
                pass
        
        # Get mood trend
        if 'mood' in self.systems:
            try:
                status['mood_trend'] = self.systems['mood'].get_mood_trend(days=7)
            except:
                pass
        
        return status


# =======================
# GLOBAL INSTANCE
# =======================
_core = None

def get_core() -> AiDCore:
    """Get or create core instance."""
    global _core
    if _core is None:
        _core = AiDCore()
        _core.initialize_all()
    return _core

def process_user_message(message: str, user: str = "User") -> Dict:
    """Process user message through all systems."""
    return get_core().process_message(message, user)

def finalize_interaction(user_msg: str, aid_response: str):
    """Finalize after AiD responds."""
    get_core().post_response_processing(user_msg, aid_response)

def start_proactive(send_callback):
    """Start proactive systems with callback."""
    get_core().start_proactive_systems(send_callback)

def shutdown_all():
    """Shutdown all systems."""
    get_core().shutdown()

def get_status() -> Dict:
    """Get system status."""
    return get_core().get_system_status()


# =======================
# EXAMPLE USAGE
# =======================
if __name__ == "__main__":
    print("AiD Core Integration - Example Usage\n")
    
    # Initialize
    core = get_core()
    
    # Example message processing
    context = process_user_message(
        "I just finished implementing the memory system! It was challenging but I did it.",
        "Dee"
    )
    
    print("\nContext generated:")
    print(f"  Memory context: {len(context['memory_context'])} memories")
    print(f"  Goals context: {len(context['goals_context'])} goals")
    if context['mood_context']:
        print(f"  Mood trend: {context['mood_context']['trend']}")
    
    # Simulate AiD's response
    aid_response = "Brilliant work, boss! That's proper impressive. How're you feelin' about it?"
    
    finalize_interaction(context['message'], aid_response)
    
    # Get status
    status = get_status()
    print(f"\nSystem Status:")
    print(f"  Active systems: {status['system_count']}")
    print(f"  Systems: {', '.join(status['active_systems'])}")
