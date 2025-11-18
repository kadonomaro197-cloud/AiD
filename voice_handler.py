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
        self.ffmpeg_available = False

        # Discord voice channel support
        self.voice_client = None
        self.is_in_voice = False
        self.current_voice_channel = None

        self._check_ffmpeg()
        self._init_tts()
        self._init_stt()

    def _check_ffmpeg(self):
        """Check if FFmpeg is installed and available."""
        import subprocess
        import shutil

        print("[VOICE DEBUG] Checking FFmpeg availability...")

        # Method 1: Check if ffmpeg command exists
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            print(f"[VOICE DEBUG] FFmpeg found at: {ffmpeg_path}")
            self.ffmpeg_available = True
        else:
            print("[VOICE WARNING] FFmpeg not found in PATH")
            self.ffmpeg_available = False

        # Method 2: Try to get FFmpeg version
        if self.ffmpeg_available:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    print(f"[VOICE DEBUG] {version_line}")
                    self.ffmpeg_available = True
                else:
                    print("[VOICE WARNING] FFmpeg found but failed to execute")
                    self.ffmpeg_available = False
            except subprocess.TimeoutExpired:
                print("[VOICE WARNING] FFmpeg check timed out")
                self.ffmpeg_available = False
            except Exception as e:
                print(f"[VOICE WARNING] FFmpeg check error: {e}")
                self.ffmpeg_available = False

        if self.ffmpeg_available:
            print("[VOICE] ✅ FFmpeg is available for Discord voice streaming")
        else:
            print("[VOICE] ⚠️ FFmpeg NOT available - Discord voice will NOT work")
            print("[VOICE] ⚠️ Install FFmpeg from: https://ffmpeg.org/download.html")
            print("[VOICE] ⚠️ Make sure FFmpeg is added to your system PATH")

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

            print("[VOICE DEBUG] TTS module imported successfully")

            # Load reference audio samples
            print(f"[VOICE DEBUG] Loading reference audio from: {self.voice_samples_dir}")
            self.reference_audio = self._load_reference_audio()

            if not self.reference_audio:
                print(f"[VOICE ERROR] No reference audio found in {self.voice_samples_dir}")
                print("[VOICE ERROR] Voice cloning requires reference audio samples")
                print("[VOICE ERROR] See VOICE_CLONING_GUIDE.md for setup instructions")
                return False

            print(f"[VOICE DEBUG] Found {len(self.reference_audio)} reference samples:")
            for i, sample in enumerate(self.reference_audio):
                print(f"[VOICE DEBUG]   [{i}] {sample}")

            # Initialize Coqui TTS with voice cloning model
            # Using XTTS v2 - supports voice cloning with reference audio
            print("[VOICE DEBUG] Loading XTTS v2 model (this may take a moment)...")
            try:
                self.tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                print("[VOICE DEBUG] XTTS v2 model loaded successfully")
            except Exception as model_error:
                print(f"[VOICE ERROR] Failed to load XTTS v2 model: {model_error}")
                import traceback
                traceback.print_exc()
                return False

            self.tts_mode = 'coqui'
            self.tts_enabled = True

            print(f"[VOICE] ✅ TTS initialized with Coqui TTS (voice cloning)")
            print(f"[VOICE] ✅ Using {len(self.reference_audio)} reference sample(s)")

            return True

        except ImportError as import_error:
            print(f"[VOICE ERROR] Coqui TTS not available: {import_error}")
            print("[VOICE ERROR] Install with: pip install TTS")
            return False
        except Exception as e:
            print(f"[VOICE ERROR] Coqui TTS initialization error: {e}")
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

            print(f"[VOICE DEBUG] _speak_coqui called with play_audio={play_audio}")

            # Select reference audio based on config
            ref_index = VoiceConfig.REFERENCE_SAMPLE_INDEX
            if ref_index == -1:
                import random
                speaker_wav = random.choice(self.reference_audio)
                print(f"[VOICE DEBUG] Using random reference sample: {speaker_wav}")
            else:
                speaker_wav = self.reference_audio[ref_index % len(self.reference_audio)]
                print(f"[VOICE DEBUG] Using reference sample {ref_index}: {speaker_wav}")

            # Verify reference audio exists
            if not os.path.exists(speaker_wav):
                print(f"[VOICE ERROR] Reference audio file not found: {speaker_wav}")
                return False

            # Generate output path
            temp_created = False
            if output_file is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_file = temp_file.name
                temp_file.close()
                temp_created = True
                print(f"[VOICE DEBUG] Created temp output file: {output_file}")
            else:
                print(f"[VOICE DEBUG] Using provided output file: {output_file}")

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

                print(f"[VOICE DEBUG] Voice parameters: temp={VoiceConfig.TEMPERATURE}, "
                      f"rep_pen={VoiceConfig.REPETITION_PENALTY}, "
                      f"len_pen={VoiceConfig.LENGTH_PENALTY}, "
                      f"top_k={VoiceConfig.TOP_K}, top_p={VoiceConfig.TOP_P}, "
                      f"speed={VoiceConfig.SPEED}")
            except Exception as param_error:
                print(f"[VOICE WARNING] Error setting some parameters: {param_error}")

            print("[VOICE DEBUG] Calling Coqui TTS engine...")
            import time
            start_time = time.time()

            try:
                self.tts_engine.tts_to_file(**tts_kwargs)
                generation_time = time.time() - start_time
                print(f"[VOICE DEBUG] TTS generation completed in {generation_time:.2f}s")
            except Exception as tts_error:
                print(f"[VOICE ERROR] TTS engine failed: {tts_error}")
                import traceback
                traceback.print_exc()
                return False

            # Verify output file was created
            if not os.path.exists(output_file):
                print(f"[VOICE ERROR] Output file was not created: {output_file}")
                return False

            file_size = os.path.getsize(output_file)
            print(f"[VOICE DEBUG] Output file size: {file_size} bytes")

            if file_size == 0:
                print("[VOICE ERROR] Output file is empty")
                return False

            # Play the audio if requested (for local playback, not Discord)
            if play_audio:
                print("[VOICE DEBUG] Playing audio locally...")
                try:
                    import sounddevice as sd
                    import soundfile as sf
                    data, samplerate = sf.read(output_file)
                    print(f"[VOICE DEBUG] Audio data: {len(data)} samples at {samplerate} Hz")
                    sd.play(data, samplerate)
                    sd.wait()
                    print("[VOICE DEBUG] Audio playback completed")
                except ImportError:
                    print("[VOICE WARNING] sounddevice/soundfile not installed for audio playback")
                    print("[VOICE WARNING] Install with: pip install sounddevice soundfile")
                except Exception as playback_error:
                    print(f"[VOICE ERROR] Audio playback failed: {playback_error}")
                    import traceback
                    traceback.print_exc()

            # Clean up temp file if created and not needed
            if temp_created and play_audio:
                try:
                    os.remove(output_file)
                    print(f"[VOICE DEBUG] Cleaned up temp file: {output_file}")
                except Exception as cleanup_error:
                    print(f"[VOICE WARNING] Failed to cleanup temp file: {cleanup_error}")

            return True

        except Exception as e:
            print(f"[VOICE ERROR] Coqui TTS error: {e}")
            import traceback
            traceback.print_exc()
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
            'stt': self.stt_enabled,
            'ffmpeg': self.ffmpeg_available,
            'discord_voice_ready': self.tts_enabled and self.ffmpeg_available and self.tts_mode == 'coqui'
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
        temp_path = None
        try:
            import discord
            import asyncio
            import tempfile

            print(f"[VOICE DEBUG] Starting speak_in_voice for text: '{text[:50]}...'")
            print(f"[VOICE DEBUG] TTS mode: {self.tts_mode}, TTS enabled: {self.tts_enabled}")
            print(f"[VOICE DEBUG] Voice client connected: {self.voice_client and self.voice_client.is_connected()}")
            print(f"[VOICE DEBUG] FFmpeg available: {self.ffmpeg_available}")

            if not self.ffmpeg_available:
                print("[VOICE ERROR] FFmpeg is not available - cannot stream to Discord")
                print("[VOICE ERROR] Install FFmpeg and add to PATH: https://ffmpeg.org/download.html")
                return False

            if not self.voice_client or not self.voice_client.is_connected():
                print("[VOICE ERROR] Not in a voice channel")
                return False

            if not self.tts_enabled:
                print(f"[VOICE ERROR] TTS not enabled. Mode: {self.tts_mode}")
                if self.tts_mode == 'pyttsx3':
                    print("[VOICE ERROR] System is using pyttsx3 fallback instead of Coqui TTS")
                    print("[VOICE ERROR] This means Coqui TTS failed to initialize")
                return False

            # Clean text for speech
            clean_text = self._clean_for_speech(text)
            print(f"[VOICE DEBUG] Cleaned text: '{clean_text[:50]}...'")

            # Apply emotion-based voice parameters if emotion provided
            if emotion:
                try:
                    from emotion_voice_mapper import set_voice_for_emotion
                    print(f"[VOICE DEBUG] Applying emotion: {emotion} with intensity: {intensity:.2f}")
                    set_voice_for_emotion(emotion, intensity)
                    print(f"[VOICE] Applied emotion: {emotion} (intensity: {intensity:.2f})")
                except ImportError:
                    print("[VOICE WARNING] Emotion voice mapper not available, using default parameters")
                except Exception as e:
                    print(f"[VOICE ERROR] Failed to apply emotion parameters: {e}")
                    import traceback
                    traceback.print_exc()

            # Generate speech to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name

            print(f"[VOICE DEBUG] Created temp file: {temp_path}")

            # Generate the audio (don't play it locally, we'll stream to Discord)
            if self.tts_mode == 'coqui':
                print("[VOICE DEBUG] Generating audio with Coqui TTS...")
                success = self._speak_coqui(clean_text, output_file=temp_path, play_audio=False)
                print(f"[VOICE DEBUG] Coqui TTS generation result: {success}")
            else:
                # pyttsx3 can't easily save to file, so we'll skip voice for fallback
                print(f"[VOICE ERROR] Cannot use {self.tts_mode} for Discord voice streaming")
                print("[VOICE ERROR] pyttsx3 doesn't support Discord voice streaming")
                print("[VOICE ERROR] Coqui TTS is required for Discord voice. Check installation.")
                return False

            if not success:
                print("[VOICE ERROR] Failed to generate speech audio file")
                return False

            # Verify the file was created and has content
            if not os.path.exists(temp_path):
                print(f"[VOICE ERROR] Temp audio file was not created: {temp_path}")
                return False

            file_size = os.path.getsize(temp_path)
            print(f"[VOICE DEBUG] Generated audio file size: {file_size} bytes")

            if file_size == 0:
                print("[VOICE ERROR] Generated audio file is empty")
                return False

            # Check FFmpeg availability
            print("[VOICE DEBUG] Attempting to create FFmpeg audio source...")
            try:
                audio_source = discord.FFmpegPCMAudio(temp_path)
                print("[VOICE DEBUG] FFmpeg audio source created successfully")
            except Exception as ffmpeg_error:
                print(f"[VOICE ERROR] Failed to create FFmpeg audio source: {ffmpeg_error}")
                print("[VOICE ERROR] FFmpeg may not be installed or not in PATH")
                print("[VOICE ERROR] Install FFmpeg: https://ffmpeg.org/download.html")
                return False

            # Play the audio in Discord voice channel
            if self.voice_client.is_playing():
                print("[VOICE DEBUG] Stopping current audio playback")
                self.voice_client.stop()

            print("[VOICE DEBUG] Starting audio playback...")
            self.voice_client.play(audio_source)

            # Wait for playback to finish
            playback_timeout = 30  # 30 second timeout
            elapsed = 0
            while self.voice_client.is_playing():
                await asyncio.sleep(0.1)
                elapsed += 0.1
                if elapsed > playback_timeout:
                    print("[VOICE WARNING] Playback timeout exceeded")
                    break

            print(f"[VOICE DEBUG] Playback completed after {elapsed:.1f}s")

            # Clean up temp file
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                    print(f"[VOICE DEBUG] Cleaned up temp file: {temp_path}")
            except Exception as cleanup_error:
                print(f"[VOICE WARNING] Failed to cleanup temp file: {cleanup_error}")

            print(f"[VOICE] ✅ Successfully spoke in voice channel: '{clean_text[:50]}...'")
            return True

        except ImportError as e:
            print(f"[VOICE ERROR] Missing dependency for Discord voice: {e}")
            print("[VOICE ERROR] Install: pip install discord.py[voice]")
            print("[VOICE ERROR] Install FFmpeg: https://ffmpeg.org/download.html")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"[VOICE ERROR] Unexpected error in speak_in_voice: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Ensure temp file cleanup even on error
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

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
