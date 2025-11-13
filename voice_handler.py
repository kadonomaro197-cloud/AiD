"""
Voice Handler - Phase 4-5
Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities

NOTE: This is a stub implementation. Full implementation requires:
- TTS: pyttsx3, gTTS, or Coqui TTS
- STT: speech_recognition, faster-whisper, or whisper

Install dependencies:
pip install pyttsx3 SpeechRecognition pyaudio
"""

from typing import Optional


class VoiceHandler:
    """
    Manages voice input/output for AiD.
    """
    
    def __init__(self):
        self.tts_enabled = False
        self.stt_enabled = False
        self.tts_engine = None
        self.stt_recognizer = None
        
        self._init_tts()
        self._init_stt()
    
    def _init_tts(self):
        """Initialize Text-to-Speech."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Set properties for female British voice
            voices = self.tts_engine.getProperty('voices')
            # Try to find a British female voice
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            # Set rate and volume
            self.tts_engine.setProperty('rate', 175)  # Speaking rate
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            self.tts_enabled = True
            print("[VOICE] TTS initialized with pyttsx3")
        
        except ImportError:
            print("[VOICE] TTS not available (install pyttsx3)")
        except Exception as e:
            print(f"[VOICE] TTS initialization error: {e}")
    
    def _init_stt(self):
        """Initialize Speech-to-Text."""
        try:
            import speech_recognition as sr
            self.stt_recognizer = sr.Recognizer()
            self.stt_enabled = True
            print("[VOICE] STT initialized with speech_recognition")
        
        except ImportError:
            print("[VOICE] STT not available (install SpeechRecognition)")
        except Exception as e:
            print(f"[VOICE] STT initialization error: {e}")
    
    def speak(self, text: str) -> bool:
        """
        Speak text aloud.
        
        Args:
            text: Text to speak
        
        Returns:
            True if successful
        """
        if not self.tts_enabled or not self.tts_engine:
            print(f"[VOICE] TTS not available: {text[:50]}...")
            return False
        
        try:
            # Clean text for speech
            clean_text = self._clean_for_speech(text)
            
            # Speak
            self.tts_engine.say(clean_text)
            self.tts_engine.runAndWait()
            
            return True
        
        except Exception as e:
            print(f"[VOICE] TTS error: {e}")
            return False
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """
        Listen for speech input.
        
        Args:
            timeout: Seconds to listen
        
        Returns:
            Transcribed text or None
        """
        if not self.stt_enabled or not self.stt_recognizer:
            print("[VOICE] STT not available")
            return None
        
        try:
            import speech_recognition as sr
            
            with sr.Microphone() as source:
                print("[VOICE] Listening...")
                
                # Adjust for ambient noise
                self.stt_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen
                audio = self.stt_recognizer.listen(source, timeout=timeout)
                
                print("[VOICE] Processing...")
                
                # Recognize using Google Speech Recognition
                text = self.stt_recognizer.recognize_google(audio)
                
                print(f"[VOICE] Heard: {text}")
                return text
        
        except sr.WaitTimeoutError:
            print("[VOICE] Listening timeout")
            return None
        except sr.UnknownValueError:
            print("[VOICE] Could not understand audio")
            return None
        except Exception as e:
            print(f"[VOICE] STT error: {e}")
            return None
    
    def _clean_for_speech(self, text: str) -> str:
        """Clean text for natural speech."""
        # Remove markdown formatting
        clean = text.replace('*', '').replace('_', '').replace('`', '')
        
        # Remove URLs
        import re
        clean = re.sub(r'http[s]?://\S+', '', clean)
        
        # Remove emojis (TTS doesn't handle them well)
        clean = re.sub(r'[^\w\s\.,!?;:\'\"-]', '', clean)
        
        return clean
    
    def set_voice_properties(self, rate: Optional[int] = None, 
                           volume: Optional[float] = None):
        """
        Adjust voice properties.
        
        Args:
            rate: Speaking rate (words per minute)
            volume: Volume (0.0 to 1.0)
        """
        if not self.tts_engine:
            return
        
        if rate is not None:
            self.tts_engine.setProperty('rate', rate)
            print(f"[VOICE] Rate set to {rate}")
        
        if volume is not None:
            self.tts_engine.setProperty('volume', volume)
            print(f"[VOICE] Volume set to {volume}")
    
    def is_available(self) -> dict:
        """Check what voice features are available."""
        return {
            'tts': self.tts_enabled,
            'stt': self.stt_enabled
        }


# =======================
# GLOBAL INSTANCE
# =======================
_voice = None

def get_voice() -> VoiceHandler:
    """Get or create voice handler instance."""
    global _voice
    if _voice is None:
        _voice = VoiceHandler()
    return _voice

def init_voice():
    """Initialize voice handler."""
    get_voice()
    print("[VOICE] Voice handler initialized")

def speak(text: str) -> bool:
    """Speak text aloud."""
    return get_voice().speak(text)

def listen(timeout: int = 5) -> Optional[str]:
    """Listen for speech input."""
    return get_voice().listen(timeout)

def is_voice_available() -> dict:
    """Check voice availability."""
    return get_voice().is_available()
