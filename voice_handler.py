"""
Voice Handler - Phase 4-5
Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities

Supports:
- TTS: Coqui TTS with voice cloning (preferred) or pyttsx3 (fallback)
- STT: speech_recognition, faster-whisper, or whisper

Install dependencies:
pip install TTS pyttsx3 SpeechRecognition pyaudio
"""

from typing import Optional
import os
from pathlib import Path


class VoiceHandler:
    """
    Manages voice input/output for AiD.
    Supports voice cloning via Coqui TTS with reference audio.
    """

    def __init__(self):
        self.tts_enabled = False
        self.stt_enabled = False
        self.tts_engine = None
        self.tts_mode = None  # 'coqui' or 'pyttsx3'
        self.stt_recognizer = None
        self.voice_samples_dir = Path(__file__).parent / "voice_samples" / "reference"
        self.reference_audio = None

        self._init_tts()
        self._init_stt()
    
    def _init_tts(self):
        """Initialize Text-to-Speech (Coqui preferred, pyttsx3 fallback)."""
        # Try Coqui TTS with voice cloning first
        if self._init_coqui_tts():
            return

        # Fallback to pyttsx3
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_mode = 'pyttsx3'

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
            print("[VOICE] TTS initialized with pyttsx3 (fallback)")

        except ImportError:
            print("[VOICE] TTS not available (install TTS or pyttsx3)")
        except Exception as e:
            print(f"[VOICE] TTS initialization error: {e}")

    def _init_coqui_tts(self) -> bool:
        """Initialize Coqui TTS with voice cloning."""
        try:
            from TTS.api import TTS

            # Load reference audio samples
            self.reference_audio = self._load_reference_audio()

            if not self.reference_audio:
                print("[VOICE] No reference audio found in voice_samples/reference/")
                print("[VOICE] See VOICE_CLONING_GUIDE.md for setup instructions")
                return False

            # Initialize Coqui TTS with voice cloning model
            # Using XTTS v2 - supports voice cloning with reference audio
            self.tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            self.tts_mode = 'coqui'
            self.tts_enabled = True

            print(f"[VOICE] TTS initialized with Coqui TTS (voice cloning)")
            print(f"[VOICE] Using {len(self.reference_audio)} reference sample(s)")

            return True

        except ImportError:
            print("[VOICE] Coqui TTS not available (install TTS)")
            return False
        except Exception as e:
            print(f"[VOICE] Coqui TTS initialization error: {e}")
            return False

    def _load_reference_audio(self) -> Optional[list]:
        """Load reference audio samples from voice_samples/reference/."""
        if not self.voice_samples_dir.exists():
            return None

        # Supported audio formats
        audio_formats = ['.wav', '.mp3', '.flac', '.ogg']

        samples = []
        for audio_file in self.voice_samples_dir.iterdir():
            if audio_file.suffix.lower() in audio_formats:
                samples.append(str(audio_file))

        return samples if samples else None
    
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
    
    def speak(self, text: str, output_file: Optional[str] = None) -> bool:
        """
        Speak text aloud.

        Args:
            text: Text to speak
            output_file: Optional path to save audio file (Coqui only)

        Returns:
            True if successful
        """
        if not self.tts_enabled or not self.tts_engine:
            print(f"[VOICE] TTS not available: {text[:50]}...")
            return False

        try:
            # Clean text for speech
            clean_text = self._clean_for_speech(text)

            if self.tts_mode == 'coqui':
                return self._speak_coqui(clean_text, output_file)
            else:
                return self._speak_pyttsx3(clean_text)

        except Exception as e:
            print(f"[VOICE] TTS error: {e}")
            return False

    def _speak_coqui(self, text: str, output_file: Optional[str] = None) -> bool:
        """Speak using Coqui TTS with voice cloning."""
        try:
            import sounddevice as sd
            import soundfile as sf
            import tempfile

            # Use first reference audio for voice cloning
            speaker_wav = self.reference_audio[0]

            # Generate output path
            if output_file is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_file = temp_file.name
                temp_file.close()

            # Generate speech with voice cloning
            self.tts_engine.tts_to_file(
                text=text,
                speaker_wav=speaker_wav,
                language="en",
                file_path=output_file
            )

            # Play the audio
            data, samplerate = sf.read(output_file)
            sd.play(data, samplerate)
            sd.wait()

            # Clean up temp file if created
            if output_file.startswith(tempfile.gettempdir()):
                os.remove(output_file)

            return True

        except ImportError:
            print("[VOICE] sounddevice/soundfile not installed for audio playback")
            print("[VOICE] Install with: pip install sounddevice soundfile")
            return False
        except Exception as e:
            print(f"[VOICE] Coqui TTS error: {e}")
            return False

    def _speak_pyttsx3(self, text: str) -> bool:
        """Speak using pyttsx3."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"[VOICE] pyttsx3 error: {e}")
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
            'tts_mode': self.tts_mode,
            'voice_cloning': self.tts_mode == 'coqui',
            'reference_samples': len(self.reference_audio) if self.reference_audio else 0,
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
