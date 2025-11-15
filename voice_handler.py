"""
Voice Handler - Advanced TTS/STT with Discord Integration
Text-to-Speech using Coqui XTTSv2 with voice cloning
Speech-to-Text using OpenAI Whisper
Discord voice channel integration

Features:
- Voice cloning with custom samples
- Discord voice channel join/leave
- Dual output (voice + text chat)
- Async audio processing
- Voice activity detection
"""

import os
import asyncio
import discord
from discord import FFmpegPCMAudio
import torch
import numpy as np
from pathlib import Path
from typing import Optional, List
import threading
import queue
import io
import tempfile
import time
import wave

# TTS imports
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("[VOICE] TTS library not available. Install with: pip install TTS")

# STT imports
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("[VOICE] Whisper not available. Install with: pip install openai-whisper")

# Audio processing
try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("[VOICE] Audio libraries not available. Install with: pip install sounddevice soundfile")


# =======================
# CONFIGURATION
# =======================
VOICE_SAMPLES_DIR = Path(__file__).parent / "voice_samples"
TTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
WHISPER_MODEL_SIZE = "base"  # tiny, base, small, medium, large
SAMPLE_RATE = 24000  # XTTSv2 uses 24kHz
DISCORD_SAMPLE_RATE = 48000  # Discord expects 48kHz
TEMP_AUDIO_DIR = Path(__file__).parent / "temp_audio"

# Ensure directories exist
VOICE_SAMPLES_DIR.mkdir(exist_ok=True)
TEMP_AUDIO_DIR.mkdir(exist_ok=True)


# =======================
# TEXT-TO-SPEECH ENGINE
# =======================
class TextToSpeechEngine:
    """
    Coqui XTTSv2 TTS Engine with voice cloning.
    """

    def __init__(self):
        self.tts = None
        self.is_initialized = False
        self.is_speaking = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.voice_samples = []
        self.speaker_embedding = None
        self.gpt_cond_latent = None

    def initialize(self) -> bool:
        """Initialize TTS engine and load voice samples."""
        if not TTS_AVAILABLE:
            print("[TTS] Coqui TTS not available")
            return False

        try:
            print(f"[TTS] Loading XTTSv2 model on {self.device}...")
            self.tts = TTS(TTS_MODEL_NAME).to(self.device)

            # Load voice samples
            self._load_voice_samples()

            self.is_initialized = True
            print("[TTS] ✓ XTTSv2 initialized successfully")
            return True

        except Exception as e:
            print(f"[TTS] Initialization error: {e}")
            return False

    def _load_voice_samples(self):
        """Load all WAV files from voice_samples directory."""
        wav_files = list(VOICE_SAMPLES_DIR.glob("*.wav"))

        if not wav_files:
            print(f"[TTS] WARNING: No voice samples found in {VOICE_SAMPLES_DIR}")
            print("[TTS] Please add WAV files to the voice_samples directory for voice cloning")
            return

        self.voice_samples = [str(f) for f in wav_files]
        print(f"[TTS] Found {len(self.voice_samples)} voice sample(s):")
        for sample in self.voice_samples:
            print(f"  - {Path(sample).name}")

    def synthesize(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Synthesize speech from text.

        Args:
            text: Text to speak
            output_path: Optional path to save audio file

        Returns:
            Path to generated audio file
        """
        if not self.is_initialized:
            print("[TTS] Engine not initialized")
            return None

        try:
            self.is_speaking = True

            # Clean text
            clean_text = self._clean_for_tts(text)

            if not clean_text.strip():
                print("[TTS] Empty text after cleaning")
                return None

            # Generate output path if not provided
            if output_path is None:
                timestamp = int(time.time() * 1000)
                output_path = str(TEMP_AUDIO_DIR / f"tts_{timestamp}.wav")

            # Synthesize with voice cloning
            if self.voice_samples:
                # Use first sample as reference for voice cloning
                # XTTSv2 can use multiple samples, but we'll use the first for simplicity
                print(f"[TTS] Generating speech with voice cloning...")
                self.tts.tts_to_file(
                    text=clean_text,
                    file_path=output_path,
                    speaker_wav=self.voice_samples[0],
                    language="en"
                )
            else:
                # Fallback to default voice
                print("[TTS] Generating speech with default voice...")
                self.tts.tts_to_file(
                    text=clean_text,
                    file_path=output_path,
                    language="en"
                )

            self.is_speaking = False
            print(f"[TTS] Audio generated: {output_path}")
            return output_path

        except Exception as e:
            print(f"[TTS] Synthesis error: {e}")
            self.is_speaking = False
            return None

    def _clean_for_tts(self, text: str) -> str:
        """Clean text for better TTS output."""
        import re

        # Remove markdown formatting
        text = text.replace("*", "")
        text = text.replace("_", "")
        text = text.replace("`", "")
        text = text.replace("#", "")

        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)

        # Remove emojis (keep text only)
        text = re.sub(r'[^\w\s\.,!?\'\"-]', '', text)

        # Replace common slang for better pronunciation
        replacements = {
            "innit": "isn't it",
            "ya": "you",
            "gonna": "going to",
            "wanna": "want to",
            "dunno": "don't know",
            "kinda": "kind of",
            "sorta": "sort of",
        }

        for old, new in replacements.items():
            text = re.sub(r'\b' + old + r'\b', new, text, flags=re.IGNORECASE)

        return text.strip()


# =======================
# SPEECH-TO-TEXT ENGINE
# =======================
class SpeechToTextEngine:
    """
    Whisper STT Engine for voice recognition.
    """

    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.is_listening = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def initialize(self) -> bool:
        """Initialize Whisper model."""
        if not WHISPER_AVAILABLE:
            print("[STT] Whisper not available")
            return False

        try:
            print(f"[STT] Loading Whisper {WHISPER_MODEL_SIZE} model on {self.device}...")
            self.model = whisper.load_model(WHISPER_MODEL_SIZE, device=self.device)
            self.is_initialized = True
            print("[STT] ✓ Whisper initialized successfully")
            return True

        except Exception as e:
            print(f"[STT] Initialization error: {e}")
            return False

    def transcribe_file(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text or None
        """
        if not self.is_initialized:
            print("[STT] Engine not initialized")
            return None

        try:
            print(f"[STT] Transcribing: {audio_path}")
            result = self.model.transcribe(audio_path, language="en")
            text = result["text"].strip()
            print(f"[STT] Transcribed: {text}")
            return text

        except Exception as e:
            print(f"[STT] Transcription error: {e}")
            return None

    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
        """
        Transcribe raw audio data.

        Args:
            audio_data: NumPy array of audio samples
            sample_rate: Sample rate of audio

        Returns:
            Transcribed text or None
        """
        if not self.is_initialized:
            return None

        try:
            # Whisper expects float32 audio normalized to [-1, 1]
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32) / np.iinfo(audio_data.dtype).max

            # Resample to 16kHz if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                # Simple resampling (for production, use librosa or scipy)
                audio_data = audio_data[::int(sample_rate/16000)]

            result = self.model.transcribe(audio_data, language="en")
            return result["text"].strip()

        except Exception as e:
            print(f"[STT] Transcription error: {e}")
            return None


# =======================
# DISCORD VOICE HANDLER
# =======================
class DiscordVoiceHandler:
    """
    Handles Discord voice channel integration.
    """

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.voice_client: Optional[discord.VoiceClient] = None
        self.current_channel: Optional[discord.VoiceChannel] = None
        self.text_channel: Optional[discord.TextChannel] = None
        self.is_in_voice = False
        self.audio_queue = asyncio.Queue()
        self.playback_task = None

    async def join_voice_channel(self, user_voice_channel: discord.VoiceChannel, text_channel: discord.TextChannel) -> bool:
        """
        Join a Discord voice channel.

        Args:
            user_voice_channel: Voice channel to join
            text_channel: Text channel for dual output

        Returns:
            True if successful
        """
        try:
            # Disconnect from current channel if connected
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()

            # Join the voice channel
            self.voice_client = await user_voice_channel.connect()
            self.current_channel = user_voice_channel
            self.text_channel = text_channel
            self.is_in_voice = True

            # Start playback task
            if self.playback_task is None or self.playback_task.done():
                self.playback_task = asyncio.create_task(self._audio_playback_loop())

            print(f"[VOICE] Joined voice channel: {user_voice_channel.name}")
            return True

        except Exception as e:
            print(f"[VOICE] Error joining voice channel: {e}")
            return False

    async def leave_voice_channel(self) -> bool:
        """
        Leave the current voice channel.

        Returns:
            True if successful
        """
        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()

            self.voice_client = None
            self.current_channel = None
            self.is_in_voice = False

            # Cancel playback task
            if self.playback_task and not self.playback_task.done():
                self.playback_task.cancel()

            print("[VOICE] Left voice channel")
            return True

        except Exception as e:
            print(f"[VOICE] Error leaving voice channel: {e}")
            return False

    async def play_audio_file(self, audio_path: str, text: str = ""):
        """
        Queue audio file for playback in voice channel.

        Args:
            audio_path: Path to audio file
            text: Original text (for dual output to text channel)
        """
        await self.audio_queue.put((audio_path, text))

    async def _audio_playback_loop(self):
        """Background task for playing queued audio."""
        while self.is_in_voice:
            try:
                # Get next audio file from queue
                audio_path, text = await asyncio.wait_for(self.audio_queue.get(), timeout=1.0)

                # Send text to text channel (dual output)
                if self.text_channel and text:
                    await self.text_channel.send(f"🎙️ {text}")

                # Play audio in voice channel
                if self.voice_client and self.voice_client.is_connected():
                    # Convert 24kHz to 48kHz for Discord
                    converted_path = self._convert_audio_for_discord(audio_path)

                    # Play audio
                    audio_source = FFmpegPCMAudio(converted_path)
                    self.voice_client.play(audio_source)

                    # Wait for playback to finish
                    while self.voice_client.is_playing():
                        await asyncio.sleep(0.1)

                    # Clean up converted file
                    try:
                        os.remove(converted_path)
                    except:
                        pass

                # Clean up original file
                try:
                    os.remove(audio_path)
                except:
                    pass

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[VOICE] Playback error: {e}")

    def _convert_audio_for_discord(self, input_path: str) -> str:
        """
        Convert audio to Discord-compatible format (48kHz, stereo, 16-bit PCM).

        Args:
            input_path: Input audio file

        Returns:
            Path to converted audio file
        """
        output_path = str(TEMP_AUDIO_DIR / f"discord_{Path(input_path).name}")

        # Use ffmpeg to convert
        os.system(f'ffmpeg -i "{input_path}" -ar {DISCORD_SAMPLE_RATE} -ac 2 -y "{output_path}" -loglevel quiet')

        return output_path


# =======================
# MAIN VOICE MANAGER
# =======================
class VoiceManager:
    """
    Main voice manager coordinating TTS, STT, and Discord integration.
    """

    def __init__(self, bot: Optional[discord.Client] = None):
        self.tts_engine = TextToSpeechEngine()
        self.stt_engine = SpeechToTextEngine()
        self.discord_voice = DiscordVoiceHandler(bot) if bot else None
        self.is_initialized = False
        self.voice_mode_enabled = False

    def initialize(self) -> dict:
        """
        Initialize all voice components.

        Returns:
            Dictionary with initialization status
        """
        print("[VOICE] Initializing voice system...")

        tts_ok = self.tts_engine.initialize()
        stt_ok = self.stt_engine.initialize()

        self.is_initialized = tts_ok or stt_ok

        status = {
            'tts': tts_ok,
            'stt': stt_ok,
            'discord': self.discord_voice is not None,
            'initialized': self.is_initialized
        }

        print(f"[VOICE] Initialization complete: TTS={tts_ok}, STT={stt_ok}")
        return status

    async def speak(self, text: str, send_to_voice: bool = True) -> bool:
        """
        Generate speech from text.

        Args:
            text: Text to speak
            send_to_voice: If True and in voice channel, play in Discord

        Returns:
            True if successful
        """
        if not self.tts_engine.is_initialized:
            print("[VOICE] TTS not initialized")
            return False

        # Generate audio
        audio_path = self.tts_engine.synthesize(text)

        if not audio_path:
            return False

        # Play in Discord voice channel if enabled
        if send_to_voice and self.discord_voice and self.discord_voice.is_in_voice:
            await self.discord_voice.play_audio_file(audio_path, text)
        else:
            # Clean up file if not playing in Discord
            try:
                os.remove(audio_path)
            except:
                pass

        return True

    async def listen_from_file(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text or None
        """
        if not self.stt_engine.is_initialized:
            print("[VOICE] STT not initialized")
            return None

        return self.stt_engine.transcribe_file(audio_path)

    async def join_voice(self, voice_channel: discord.VoiceChannel, text_channel: discord.TextChannel) -> bool:
        """Join Discord voice channel."""
        if not self.discord_voice:
            print("[VOICE] Discord voice not available")
            return False

        success = await self.discord_voice.join_voice_channel(voice_channel, text_channel)
        if success:
            self.voice_mode_enabled = True
        return success

    async def leave_voice(self) -> bool:
        """Leave Discord voice channel."""
        if not self.discord_voice:
            return False

        success = await self.discord_voice.leave_voice_channel()
        if success:
            self.voice_mode_enabled = False
        return success

    def is_in_voice_channel(self) -> bool:
        """Check if bot is in a voice channel."""
        return self.discord_voice and self.discord_voice.is_in_voice


# =======================
# GLOBAL INSTANCE
# =======================
_voice_manager: Optional[VoiceManager] = None


def init_voice(bot: Optional[discord.Client] = None) -> dict:
    """
    Initialize voice system.

    Args:
        bot: Discord bot instance (optional)

    Returns:
        Initialization status
    """
    global _voice_manager
    _voice_manager = VoiceManager(bot)
    return _voice_manager.initialize()


def get_voice_manager() -> Optional[VoiceManager]:
    """Get voice manager instance."""
    return _voice_manager


async def speak(text: str, send_to_voice: bool = True) -> bool:
    """
    Make AiD speak.

    Args:
        text: Text to speak
        send_to_voice: Play in Discord voice channel if connected

    Returns:
        True if successful
    """
    if _voice_manager:
        return await _voice_manager.speak(text, send_to_voice)
    return False


async def listen_from_file(audio_path: str) -> Optional[str]:
    """
    Transcribe audio file.

    Args:
        audio_path: Path to audio file

    Returns:
        Transcribed text
    """
    if _voice_manager:
        return await _voice_manager.listen_from_file(audio_path)
    return None


def is_voice_available() -> dict:
    """Check voice system availability."""
    if _voice_manager:
        return {
            'tts': _voice_manager.tts_engine.is_initialized,
            'stt': _voice_manager.stt_engine.is_initialized,
            'discord': _voice_manager.discord_voice is not None,
            'in_voice_channel': _voice_manager.is_in_voice_channel()
        }
    return {'tts': False, 'stt': False, 'discord': False, 'in_voice_channel': False}
