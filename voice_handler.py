"""
🎙️ VOICE_HANDLER.PY - Voice Communication for AiD
Text-to-Speech (TTS) and Speech-to-Text (STT) with Discord Voice Channel Integration

Features:
- Join/leave Discord voice channels
- Text-to-speech using Coqui TTS (British female voice)
- Speech-to-text using OpenAI Whisper
- Dual output: Voice TTS + Text chat for reference
- Voice commands: "switch to voice", "back to the chat"

Dependencies:
    pip install TTS openai-whisper discord.py[voice] PyNaCl sounddevice numpy scipy

Note: FFmpeg must be installed on the system for Discord voice support
"""

import asyncio
import discord
import io
import threading
import queue
import numpy as np
import sounddevice as sd
from typing import Optional, Dict
from pathlib import Path
import tempfile
import os

# =======================
# CONFIGURATION
# =======================
TTS_MODEL = "tts_models/en/vctk/vits"  # British voices available
STT_MODEL = "base"  # Whisper model: tiny, base, small, medium, large
VOICE_CHARACTER = "p225"  # Female British voice (VCTK dataset)
SAMPLE_RATE = 22050  # TTS sample rate
STT_SAMPLE_RATE = 16000  # Whisper expects 16kHz

# Voice activity detection
SILENCE_THRESHOLD = 0.01  # Volume threshold for silence
SILENCE_DURATION = 2.0  # Seconds of silence before stopping listening

# =======================
# TTS ENGINE
# =======================
class TextToSpeech:
    """Text-to-speech engine using Coqui TTS."""

    def __init__(self):
        self.tts = None
        self.is_speaking = False
        self.initialized = False
        self._init_tts()

    def _init_tts(self):
        """Initialize TTS engine."""
        try:
            from TTS.api import TTS
            print("[VOICE] Loading Coqui TTS model...")
            self.tts = TTS(TTS_MODEL)
            self.initialized = True
            print(f"[VOICE] TTS initialized with {TTS_MODEL}")
        except ImportError:
            print("[VOICE] TTS not available - install with: pip install TTS")
        except Exception as e:
            print(f"[VOICE] TTS initialization error: {e}")

    def speak_to_file(self, text: str, output_path: str) -> bool:
        """
        Generate speech and save to file.

        Args:
            text: Text to speak
            output_path: Path to save audio file

        Returns:
            True if successful
        """
        if not self.initialized or not self.tts:
            print("[VOICE] TTS not initialized")
            return False

        try:
            # Clean text for TTS
            clean_text = self._clean_for_tts(text)

            if not clean_text.strip():
                print("[VOICE] No text to speak after cleaning")
                return False

            # Generate speech
            self.is_speaking = True
            self.tts.tts_to_file(
                text=clean_text,
                speaker=VOICE_CHARACTER,
                file_path=output_path
            )
            self.is_speaking = False

            return True

        except Exception as e:
            print(f"[VOICE] TTS error: {e}")
            self.is_speaking = False
            return False

    def speak_to_array(self, text: str) -> Optional[np.ndarray]:
        """
        Generate speech as numpy array.

        Args:
            text: Text to speak

        Returns:
            Audio as numpy array or None
        """
        if not self.initialized or not self.tts:
            return None

        try:
            clean_text = self._clean_for_tts(text)

            if not clean_text.strip():
                return None

            # Generate speech
            self.is_speaking = True
            wav = self.tts.tts(text=clean_text, speaker=VOICE_CHARACTER)
            self.is_speaking = False

            return np.array(wav)

        except Exception as e:
            print(f"[VOICE] TTS array generation error: {e}")
            self.is_speaking = False
            return None

    def _clean_for_tts(self, text: str) -> str:
        """Clean text for better TTS output."""
        import re

        # Remove markdown formatting
        text = text.replace("*", "")
        text = text.replace("_", "")
        text = text.replace("#", "")
        text = text.replace("`", "")

        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)

        # Remove emojis and special characters
        text = re.sub(r'[^\w\s\.,!?\'\"-;:]', '', text)

        # Replace common slang for better pronunciation
        replacements = {
            "innit": "init",
            "ya": "you",
            "yer": "your",
            "gonna": "going to",
            "wanna": "want to",
            "dunno": "don't know",
            "gotta": "got to",
            "kinda": "kind of",
            "sorta": "sort of",
            "mate": "mate",  # Keep as is
            "blimey": "blimey",  # Keep as is
        }

        for old, new in replacements.items():
            text = text.replace(f" {old} ", f" {new} ")
            text = text.replace(f" {old.capitalize()} ", f" {new.capitalize()} ")

        return text.strip()


# =======================
# STT ENGINE
# =======================
class SpeechToText:
    """Speech-to-text engine using OpenAI Whisper."""

    def __init__(self):
        self.model = None
        self.is_listening = False
        self.initialized = False
        self._init_stt()

    def _init_stt(self):
        """Initialize STT engine."""
        try:
            import whisper
            print(f"[VOICE] Loading Whisper model ({STT_MODEL})...")
            self.model = whisper.load_model(STT_MODEL)
            self.initialized = True
            print(f"[VOICE] STT initialized with Whisper {STT_MODEL}")
        except ImportError:
            print("[VOICE] STT not available - install with: pip install openai-whisper")
        except Exception as e:
            print(f"[VOICE] STT initialization error: {e}")

    def transcribe_file(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text or None
        """
        if not self.initialized or not self.model:
            print("[VOICE] STT not initialized")
            return None

        try:
            result = self.model.transcribe(audio_path)
            return result["text"].strip()

        except Exception as e:
            print(f"[VOICE] STT transcription error: {e}")
            return None

    def transcribe_array(self, audio: np.ndarray) -> Optional[str]:
        """
        Transcribe audio numpy array to text.

        Args:
            audio: Audio as numpy array (16kHz)

        Returns:
            Transcribed text or None
        """
        if not self.initialized or not self.model:
            return None

        try:
            # Ensure audio is float32 and normalized
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Normalize if needed
            max_val = np.abs(audio).max()
            if max_val > 1.0:
                audio = audio / max_val

            result = self.model.transcribe(audio)
            return result["text"].strip()

        except Exception as e:
            print(f"[VOICE] STT array transcription error: {e}")
            return None


# =======================
# DISCORD VOICE MANAGER
# =======================
class DiscordVoiceManager:
    """Manages Discord voice channel connections and audio streaming."""

    def __init__(self, bot):
        self.bot = bot
        self.voice_client: Optional[discord.VoiceClient] = None
        self.current_channel = None
        self.is_in_voice = False
        self.tts = TextToSpeech()
        self.stt = SpeechToText()
        self.temp_dir = tempfile.gettempdir()

    async def join_voice_channel(self, message) -> bool:
        """
        Join the voice channel of the message author.

        Args:
            message: Discord message object

        Returns:
            True if successfully joined
        """
        try:
            # Check if user is in a voice channel
            if not message.author.voice:
                await message.channel.send("Oi, mate! Ya need to be in a voice channel first, innit?")
                return False

            channel = message.author.voice.channel

            # Disconnect from current voice channel if connected
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()

            # Join the voice channel
            self.voice_client = await channel.connect()
            self.current_channel = channel
            self.is_in_voice = True

            print(f"[VOICE] Joined voice channel: {channel.name}")
            return True

        except Exception as e:
            print(f"[VOICE] Error joining voice channel: {e}")
            await message.channel.send(f"Blimey, couldn't join the voice channel: {e}")
            return False

    async def leave_voice_channel(self) -> bool:
        """
        Leave the current voice channel.

        Returns:
            True if successfully left
        """
        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()
                print(f"[VOICE] Left voice channel: {self.current_channel.name if self.current_channel else 'Unknown'}")

            self.voice_client = None
            self.current_channel = None
            self.is_in_voice = False

            return True

        except Exception as e:
            print(f"[VOICE] Error leaving voice channel: {e}")
            return False

    async def speak_in_voice(self, text: str) -> bool:
        """
        Speak text in the current voice channel.

        Args:
            text: Text to speak

        Returns:
            True if successful
        """
        if not self.is_in_voice or not self.voice_client:
            print("[VOICE] Not in a voice channel")
            return False

        if not self.tts.initialized:
            print("[VOICE] TTS not initialized")
            return False

        try:
            # Generate audio file
            temp_file = os.path.join(self.temp_dir, "aid_speech.wav")

            if not self.tts.speak_to_file(text, temp_file):
                print("[VOICE] Failed to generate speech")
                return False

            # Play audio in voice channel
            if self.voice_client.is_playing():
                self.voice_client.stop()

            audio_source = discord.FFmpegPCMAudio(temp_file)
            self.voice_client.play(audio_source, after=lambda e: self._cleanup_audio(temp_file, e))

            print(f"[VOICE] Speaking in voice channel: {text[:50]}...")
            return True

        except Exception as e:
            print(f"[VOICE] Error speaking in voice: {e}")
            return False

    def _cleanup_audio(self, file_path: str, error):
        """Clean up temporary audio file after playback."""
        if error:
            print(f"[VOICE] Playback error: {error}")

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"[VOICE] Error cleaning up audio file: {e}")

    def is_available(self) -> Dict[str, bool]:
        """Check voice system availability."""
        return {
            'tts': self.tts.initialized,
            'stt': self.stt.initialized,
            'in_voice': self.is_in_voice,
            'connected': self.voice_client is not None and self.voice_client.is_connected() if self.voice_client else False
        }


# =======================
# GLOBAL VOICE MANAGER
# =======================
_voice_manager: Optional[DiscordVoiceManager] = None

def init_voice(bot) -> DiscordVoiceManager:
    """
    Initialize the voice manager.

    Args:
        bot: Discord bot instance

    Returns:
        DiscordVoiceManager instance
    """
    global _voice_manager
    _voice_manager = DiscordVoiceManager(bot)
    print("[VOICE] Discord Voice Manager initialized")
    return _voice_manager

def get_voice() -> Optional[DiscordVoiceManager]:
    """Get the voice manager instance."""
    return _voice_manager

async def speak(text: str, message=None) -> bool:
    """
    Speak text in voice channel (if connected) and send to text chat.

    Args:
        text: Text to speak and send
        message: Discord message object (for text channel)

    Returns:
        True if successful
    """
    if not _voice_manager:
        print("[VOICE] Voice manager not initialized")
        return False

    success = True

    # Speak in voice channel if connected
    if _voice_manager.is_in_voice:
        voice_success = await _voice_manager.speak_in_voice(text)
        success = success and voice_success

    # Always send to text chat for reference
    if message:
        try:
            await message.channel.send(text)
        except Exception as e:
            print(f"[VOICE] Error sending text message: {e}")
            success = False

    return success

def is_voice_available() -> Dict[str, bool]:
    """Check voice system availability."""
    if _voice_manager:
        return _voice_manager.is_available()
    return {
        'tts': False,
        'stt': False,
        'in_voice': False,
        'connected': False
    }
