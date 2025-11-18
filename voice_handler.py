"""
Voice Handler - Phase 4-5
Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities

Supports:
- TTS: Coqui TTS with voice cloning (preferred) or pyttsx3 (fallback)
- STT: speech_recognition, faster-whisper, or whisper

Install dependencies:
pip install TTS pyttsx3 SpeechRecognition pyaudio
"""

# Fix for transformers 4.30+ compatibility with TTS 0.22.0
# BeamSearchScorer was moved to transformers.generation in newer versions
# We need to patch it BEFORE TTS tries to import it
def _patch_transformers_compatibility():
    """
    Patch transformers to make BeamSearchScorer available in main namespace.
    This fixes compatibility between TTS 0.22.0 and transformers 4.30+
    """
    try:
        import sys
        import transformers

        print("[VOICE DEBUG] Checking transformers compatibility...")

        # Check if BeamSearchScorer is already available
        try:
            from transformers import BeamSearchScorer
            print("[VOICE DEBUG] BeamSearchScorer already available in transformers")
            return True
        except ImportError:
            print("[VOICE DEBUG] BeamSearchScorer not in main transformers namespace, applying patch...")

        # Not available, need to apply patch
        # Try multiple possible locations (varies by transformers version)
        BeamSearchScorer = None
        import_locations = [
            'transformers.generation.beam_search',  # transformers 4.30+
            'transformers.generation',              # transformers 4.20-4.29
            'transformers.generation_utils',        # older versions
        ]

        for location in import_locations:
            try:
                if location == 'transformers.generation.beam_search':
                    from transformers.generation.beam_search import BeamSearchScorer
                elif location == 'transformers.generation':
                    from transformers.generation import BeamSearchScorer
                elif location == 'transformers.generation_utils':
                    from transformers.generation_utils import BeamSearchScorer

                print(f"[VOICE DEBUG] Successfully imported BeamSearchScorer from {location}")
                break
            except ImportError:
                continue

        if BeamSearchScorer is None:
            print(f"[VOICE DEBUG] ✗ BeamSearchScorer not found in any known location")
            print(f"[VOICE DEBUG] transformers version: {transformers.__version__}")
            print(f"[VOICE DEBUG] Tried locations: {', '.join(import_locations)}")
            return False

        # Patch it into the transformers module's namespace
        # Multiple strategies to ensure it's accessible

        # Strategy 1: Direct attribute assignment
        transformers.BeamSearchScorer = BeamSearchScorer

        # Strategy 2: Add to module's __dict__
        transformers.__dict__['BeamSearchScorer'] = BeamSearchScorer

        # Strategy 3: Update sys.modules entry
        sys.modules['transformers'].BeamSearchScorer = BeamSearchScorer

        # Verify the patch worked
        try:
            from transformers import BeamSearchScorer as Test
            print("[VOICE DEBUG] ✓ BeamSearchScorer compatibility patch verified and working!")
            return True
        except ImportError:
            print("[VOICE DEBUG] ✗ Patch applied but verification failed")
            return False
        except Exception as e:
            print(f"[VOICE DEBUG] ✗ Unexpected error during patch: {e}")
            import traceback
            traceback.print_exc()
            return False

    except ImportError as e:
        print(f"[VOICE DEBUG] transformers not installed: {e}")
        return False
    except Exception as e:
        print(f"[VOICE DEBUG] ✗ Unexpected error in compatibility check: {e}")
        import traceback
        traceback.print_exc()
        return False

# Apply the patch when module is imported
_patch_success = _patch_transformers_compatibility()

from typing import Optional
import os
from pathlib import Path
from voice_config import VoiceConfig


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

        # Discord voice channel support
        self.voice_client = None
        self.is_in_voice = False
        self.current_voice_channel = None

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
            print("[VOICE DEBUG] Attempting to initialize Coqui TTS...")
            from TTS.api import TTS

            # Load reference audio samples
            print("[VOICE DEBUG] Loading reference audio from:", self.voice_samples_dir)
            self.reference_audio = self._load_reference_audio()

            if not self.reference_audio:
                print("[VOICE] No reference audio found in voice_samples/reference/")
                print("[VOICE] See VOICE_CLONING_GUIDE.md for setup instructions")
                return False

            print(f"[VOICE DEBUG] Found {len(self.reference_audio)} reference samples:")
            for i, ref in enumerate(self.reference_audio):
                print(f"[VOICE DEBUG]   [{i}] {ref}")

            # Initialize Coqui TTS with voice cloning model
            # Using XTTS v2 - supports voice cloning with reference audio
            print("[VOICE DEBUG] Loading XTTS v2 model (this may take a moment)...")
            self.tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            self.tts_mode = 'coqui'
            self.tts_enabled = True

            print(f"[VOICE] TTS initialized with Coqui TTS (voice cloning)")
            print(f"[VOICE] Using {len(self.reference_audio)} reference sample(s)")

            return True

        except ImportError as e:
            print(f"[VOICE ERROR] Failed to import TTS: {e}")
            print("[VOICE] Coqui TTS not available (install TTS)")
            return False
        except Exception as e:
            print(f"[VOICE ERROR] Failed to load XTTS v2 model: {e}")
            import traceback
            traceback.print_exc()
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

    def _speak_coqui(self, text: str, output_file: Optional[str] = None, play_audio: bool = True) -> bool:
        """Speak using Coqui TTS with voice cloning."""
        try:
            import tempfile

            # Select reference audio based on config
            ref_index = VoiceConfig.REFERENCE_SAMPLE_INDEX
            if ref_index == -1:
                import random
                speaker_wav = random.choice(self.reference_audio)
            else:
                speaker_wav = self.reference_audio[ref_index % len(self.reference_audio)]

            # Generate output path
            temp_created = False
            if output_file is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_file = temp_file.name
                temp_file.close()
                temp_created = True

            # Generate speech with voice cloning and configured parameters
            # Build kwargs based on what the model supports
            tts_kwargs = {
                "text": text,
                "speaker_wav": speaker_wav,
                "language": "en",
                "file_path": output_file,
            }

            # Add optional parameters (some XTTS versions may not support all)
            try:
                tts_kwargs["temperature"] = VoiceConfig.TEMPERATURE
                tts_kwargs["repetition_penalty"] = VoiceConfig.REPETITION_PENALTY
                tts_kwargs["length_penalty"] = VoiceConfig.LENGTH_PENALTY
                tts_kwargs["top_k"] = VoiceConfig.TOP_K
                tts_kwargs["top_p"] = VoiceConfig.TOP_P
                tts_kwargs["enable_text_splitting"] = VoiceConfig.ENABLE_TEXT_SPLITTING

                # Speed is not always supported
                if hasattr(VoiceConfig, 'SPEED') and VoiceConfig.SPEED != 1.0:
                    tts_kwargs["speed"] = VoiceConfig.SPEED
            except:
                pass  # If parameters not supported, use defaults

            self.tts_engine.tts_to_file(**tts_kwargs)

            # Play the audio if requested (for local playback, not Discord)
            if play_audio:
                try:
                    import sounddevice as sd
                    import soundfile as sf
                    data, samplerate = sf.read(output_file)
                    sd.play(data, samplerate)
                    sd.wait()
                except ImportError:
                    print("[VOICE] sounddevice/soundfile not installed for audio playback")
                    print("[VOICE] Install with: pip install sounddevice soundfile")

            # Clean up temp file if created and not needed
            if temp_created and play_audio:
                os.remove(output_file)

            return True

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
    # DISCORD VOICE CHANNEL INTEGRATION
    # =======================

    async def join_voice_channel(self, message) -> bool:
        """
        Join the voice channel that the message author is in.

        Args:
            message: Discord message object

        Returns:
            bool: True if successfully joined, False otherwise
        """
        try:
            # Check if user is in a voice channel
            if not message.author.voice:
                await message.channel.send("You need to be in a voice channel for me to join, innit?")
                return False

            # Get the voice channel
            voice_channel = message.author.voice.channel

            # Join the channel
            if self.voice_client and self.voice_client.is_connected():
                # Already in a voice channel, move to new one
                await self.voice_client.move_to(voice_channel)
            else:
                # Join the channel
                self.voice_client = await voice_channel.connect()

            self.is_in_voice = True
            self.current_voice_channel = voice_channel
            print(f"[VOICE] Joined voice channel: {voice_channel.name}")
            return True

        except Exception as e:
            print(f"[VOICE] Error joining voice channel: {e}")
            await message.channel.send(f"Couldn't join the voice channel: {e}")
            return False

    async def leave_voice_channel(self) -> bool:
        """
        Leave the current voice channel.

        Returns:
            bool: True if successfully left, False otherwise
        """
        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()
                print("[VOICE] Left voice channel")

            self.voice_client = None
            self.is_in_voice = False
            self.current_voice_channel = None
            return True

        except Exception as e:
            print(f"[VOICE] Error leaving voice channel: {e}")
            return False

    async def speak_in_voice(self, text: str, emotion: Optional[str] = None,
                            intensity: float = 0.5) -> bool:
        """
        Speak in Discord voice channel with emotion-aware voice parameters.

        Args:
            text: Text to speak
            emotion: Optional emotion to apply (e.g., "happy", "sad", "neutral")
            intensity: Emotion intensity (0.0 to 1.0)

        Returns:
            bool: True if successfully spoke, False otherwise
        """
        try:
            import discord
            import asyncio
            import tempfile

            if not self.voice_client or not self.voice_client.is_connected():
                print("[VOICE] Not in a voice channel")
                return False

            if not self.tts_enabled:
                print("[VOICE] TTS not enabled")
                return False

            # Clean text for speech
            clean_text = self._clean_for_speech(text)

            # Apply emotion-based voice parameters if emotion provided
            if emotion:
                try:
                    from emotion_voice_mapper import set_voice_for_emotion
                    set_voice_for_emotion(emotion, intensity)
                    print(f"[VOICE] Applied emotion: {emotion} (intensity: {intensity:.2f})")
                except ImportError:
                    print("[VOICE] Emotion voice mapper not available, using default parameters")

            # Generate speech to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name

            # Generate the audio (don't play it locally, we'll stream to Discord)
            if self.tts_mode == 'coqui':
                success = self._speak_coqui(clean_text, output_file=temp_path, play_audio=False)
            else:
                # pyttsx3 can't easily save to file, so we'll skip voice for fallback
                print("[VOICE] pyttsx3 doesn't support Discord voice streaming")
                return False

            if not success:
                print("[VOICE] Failed to generate speech")
                return False

            # Play the audio in Discord voice channel
            if self.voice_client.is_playing():
                self.voice_client.stop()

            audio_source = discord.FFmpegPCMAudio(temp_path)
            self.voice_client.play(audio_source)

            # Wait for playback to finish
            while self.voice_client.is_playing():
                await asyncio.sleep(0.1)

            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass

            print(f"[VOICE] Spoke in voice channel: '{clean_text[:50]}...'")
            return True

        except ImportError as e:
            print(f"[VOICE] Missing dependency for Discord voice: {e}")
            print("[VOICE] Install: pip install discord.py[voice] ffmpeg-python")
            return False
        except Exception as e:
            print(f"[VOICE] Error speaking in voice channel: {e}")
            import traceback
            traceback.print_exc()
            return False

    def speak_with_emotion(self, text: str, emotion: str, intensity: float = 0.5,
                          output_file: Optional[str] = None) -> bool:
        """
        Speak with specific emotion (for testing or non-Discord usage).

        Args:
            text: Text to speak
            emotion: Emotion to apply
            intensity: Emotion intensity (0.0 to 1.0)
            output_file: Optional output file path

        Returns:
            bool: True if successful
        """
        try:
            from emotion_voice_mapper import set_voice_for_emotion
            set_voice_for_emotion(emotion, intensity)
            return self.speak(text, output_file=output_file)
        except ImportError:
            print("[VOICE] Emotion voice mapper not available")
            return self.speak(text, output_file=output_file)


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
