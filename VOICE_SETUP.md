# AiD Voice System Setup Guide

Complete guide for setting up Text-to-Speech (TTS) and Speech-to-Text (STT) with voice cloning for AiD.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Voice Sample Preparation](#voice-sample-preparation)
- [Discord Bot Permissions](#discord-bot-permissions)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

---

## Overview

AiD's voice system provides:
- **TTS (Text-to-Speech)**: Custom voice cloning using Coqui XTTSv2
- **STT (Speech-to-Text)**: Voice recognition using OpenAI Whisper
- **Discord Voice Integration**: Join/leave voice channels
- **Dual Output**: Responses in both voice and text chat

---

## Requirements

### System Requirements
- **Python**: 3.9 or higher (tested on 3.11.14)
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GPU with 8GB+ VRAM recommended (CUDA 11.8+)
  - CPU-only mode works but is slower
- **Disk Space**: ~5GB for models
- **OS**: Linux, macOS, or Windows

### Software Dependencies
- **FFmpeg**: Required for audio processing and Discord voice
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

---

## Installation

### Step 1: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg portaudio19-dev python3-dev

# macOS
brew install ffmpeg portaudio

# Windows
# Download and install FFmpeg from https://ffmpeg.org/download.html
# Add FFmpeg to your PATH
```

### Step 2: Create Virtual Environment

```bash
cd /path/to/AiD
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# If you have NVIDIA GPU with CUDA, install GPU-accelerated PyTorch
# For CUDA 11.8:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 4: Verify Installation

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
python -c "from TTS.api import TTS; print('TTS OK')"
python -c "import whisper; print('Whisper OK')"
```

---

## Voice Sample Preparation

### What You Need
- **7 WAV files** with your desired voice
- **Total duration**: 8+ minutes (you have this covered!)
- **Quality**: Clear speech, minimal background noise
- **Format**: 16-bit PCM WAV, 22050 Hz or 24000 Hz sample rate

### Preparing Your Samples

1. **Check Current Format**
   ```bash
   ffmpeg -i your_sample.wav
   ```

2. **Convert to Proper Format** (if needed)
   ```bash
   # Convert to 24kHz, mono, 16-bit PCM
   ffmpeg -i input.mp3 -ar 24000 -ac 1 -sample_fmt s16 output.wav
   ```

3. **Place Samples in Directory**
   ```bash
   # Copy your samples to the voice_samples directory
   cp sample_01.wav /path/to/AiD/voice_samples/
   cp sample_02.wav /path/to/AiD/voice_samples/
   # ... etc
   ```

4. **Verify Samples**
   ```bash
   ls -lh voice_samples/
   # Should show your WAV files
   ```

### Voice Quality Tips

**Good samples have:**
- ✅ Natural, conversational speech
- ✅ Varied intonation (questions, statements, emotions)
- ✅ Consistent volume levels
- ✅ Minimal background noise
- ✅ Clear pronunciation

**Avoid:**
- ❌ Music or sound effects
- ❌ Multiple speakers
- ❌ Heavy compression
- ❌ Echo or reverb
- ❌ Very quiet or very loud sections

### Noise Reduction (Optional)

If your samples have background noise:

```bash
# Using FFmpeg
ffmpeg -i input.wav -af "highpass=f=200, lowpass=f=3000" output.wav

# Or use Audacity (GUI tool)
# 1. Open file in Audacity
# 2. Select silent section with only noise
# 3. Effect > Noise Reduction > Get Noise Profile
# 4. Select all audio
# 5. Effect > Noise Reduction > OK
```

---

## Discord Bot Permissions

### Required Intents
Ensure your Discord bot has these intents enabled in the [Discord Developer Portal](https://discord.com/developers/applications):

1. **Server Members Intent**: ✅ Enabled
2. **Presence Intent**: ✅ Enabled
3. **Message Content Intent**: ✅ Enabled

### Required Permissions
When inviting the bot, use these permissions:

- ✅ Read Messages/View Channels
- ✅ Send Messages
- ✅ Connect (Voice)
- ✅ Speak (Voice)
- ✅ Use Voice Activity

**Permission Integer**: `3165184` (or use Discord's permission calculator)

### Invite URL Template
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=3165184&scope=bot
```

---

## Usage

### Starting the Bot

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run the bot
python bot.py
```

### Voice Commands

#### Joining Voice Channel

**Method 1: Command**
```
!join_voice
```
- You must be in a voice channel first
- AiD will join your current voice channel

**Method 2: Natural Language**
```
AiD, switch to voice
AiD, go to voice
AiD, join voice
Hey AiD, voice mode please
```

#### Leaving Voice Channel

**Method 1: Command**
```
!leave_voice
```

**Method 2: Natural Language**
```
AiD, back to chat
Back to text please
Leave voice
Exit voice mode
```

#### Checking Voice Status

```
!voice_status
```

Shows:
- TTS status (enabled/disabled)
- STT status (enabled/disabled)
- Current voice channel (if connected)
- Discord integration status

### Using Voice Mode

1. **Join a voice channel** on your Discord server
2. **Say or type**: "AiD, switch to voice"
3. **AiD will**:
   - Join your voice channel
   - Confirm with a voice message
   - Respond to your messages in voice AND text
4. **Chat normally** - every response will be spoken and written
5. **To exit**: Say or type "back to chat"

### Example Conversation

```
You (in voice channel): AiD, switch to voice

AiD (in chat): 🎤 Joining voice channel: General...
AiD (in voice + chat): Voice mode enabled, boss! I can hear you now!

You: Tell me a joke

AiD (in voice + chat): Why did the AI go to therapy? Because it had too many
deep learning issues! 😄

You: Back to chat

AiD (in voice + chat): Voice mode disabled. Back to text chat!
AiD (in chat): 👋 Left voice channel. Back to text chat only!
```

---

## Troubleshooting

### Issue: "Voice system not available"

**Solution:**
```bash
# Check if TTS is installed
python -c "from TTS.api import TTS; print('TTS OK')"

# Reinstall if needed
pip install --upgrade TTS torch torchaudio
```

### Issue: "FFmpeg not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows: Add FFmpeg to PATH
# 1. Download from https://ffmpeg.org/download.html
# 2. Extract to C:\ffmpeg
# 3. Add C:\ffmpeg\bin to System PATH
```

### Issue: "CUDA out of memory"

**Solutions:**
1. **Use smaller Whisper model**
   - Edit `voice_handler.py`, line 61:
   ```python
   WHISPER_MODEL_SIZE = "tiny"  # or "base" instead of "small"
   ```

2. **Close other GPU applications**

3. **Use CPU mode**
   - The system will automatically fall back to CPU if CUDA isn't available

### Issue: "No voice samples found"

**Solution:**
```bash
# Check if samples exist
ls -la voice_samples/

# Ensure files are .wav format
# Convert if needed:
ffmpeg -i sample.mp3 -ar 24000 -ac 1 sample.wav

# Move to correct directory
mv sample*.wav voice_samples/
```

### Issue: "Bot can't join voice channel"

**Solution:**
1. Check bot permissions (needs "Connect" and "Speak")
2. Ensure you're in a voice channel first
3. Check if voice channel has user limit
4. Verify bot has necessary Discord intents enabled

### Issue: "Voice is robotic or distorted"

**Solutions:**
1. **Improve voice samples**:
   - Use longer samples (8+ minutes ideal)
   - Ensure consistent quality
   - Remove background noise

2. **Check sample rate**:
   ```bash
   ffmpeg -i voice_samples/sample_01.wav
   # Should show 24000 Hz or 22050 Hz
   ```

### Issue: "TTS is very slow"

**Solutions:**
1. **Use GPU** (if available):
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   # Should print True
   ```

2. **Reduce text length** - long responses take longer to generate

3. **Use faster model** (future option - XTTSv2 is already optimized)

---

## Performance Optimization

### GPU Optimization

**NVIDIA GPU with CUDA:**
```bash
# Install CUDA-optimized PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available(), 'Device:', torch.cuda.get_device_name(0))"
```

**Expected Performance (RTX 3090):**
- TTS generation: 2-4 seconds for ~30 words
- STT transcription: <1 second for 5-second audio
- Memory usage: ~4GB VRAM

### CPU Optimization

**If using CPU only:**
- Expect slower performance (5-10x slower)
- TTS may take 10-30 seconds per response
- Consider shorter responses

### Network Optimization

- **Local inference**: Bot uses local API (127.0.0.1:60331)
- **No internet needed** for TTS/STT (after models download)
- **First run**: Models will download (~2GB TTS, ~500MB Whisper)

---

## Testing Voice System

### Test TTS Only

```bash
python test_tts.py
```

This will:
1. Load the TTS model
2. Load your voice samples
3. Generate test audio
4. Save to `test_output.wav`

### Test in Discord

1. Start the bot: `python bot.py`
2. Check startup logs for:
   ```
   [VOICE] ✓ Voice handler module loaded
   [VOICE] Initializing voice system with bot instance...
   [VOICE] Voice system ready - TTS: True, STT: True
   Voice System: [OK] (TTS/STT ready)
   ```
3. Run `!voice_status` in Discord
4. Join voice channel and test with `!join_voice`

---

## Advanced Configuration

### Changing Voice Model

Edit `voice_handler.py`, line 60:
```python
# Use different Whisper model size
WHISPER_MODEL_SIZE = "tiny"    # Fastest, least accurate
WHISPER_MODEL_SIZE = "base"    # Fast, good accuracy (default)
WHISPER_MODEL_SIZE = "small"   # Slower, better accuracy
WHISPER_MODEL_SIZE = "medium"  # Slow, great accuracy
WHISPER_MODEL_SIZE = "large"   # Slowest, best accuracy
```

### Custom Voice Sample Selection

By default, XTTSv2 uses the first sample for voice cloning. To use a specific sample:

Edit `voice_handler.py`, line 161:
```python
# Change from:
speaker_wav=self.voice_samples[0]

# To (for example, use third sample):
speaker_wav=self.voice_samples[2]
```

### Adjusting Audio Quality

Edit `voice_handler.py` to change sample rates:
```python
SAMPLE_RATE = 24000          # XTTSv2 default (higher quality)
# or
SAMPLE_RATE = 22050          # Standard quality (smaller files)
```

---

## Support & Resources

- **AiD Discord Bot**: Contact Dee for support
- **Coqui TTS Docs**: https://docs.coqui.ai/
- **Whisper Docs**: https://github.com/openai/whisper
- **Discord.py Voice**: https://discordpy.readthedocs.io/en/stable/api.html#voice-related

---

## Credits

- **TTS**: Coqui XTTSv2 (voice cloning)
- **STT**: OpenAI Whisper
- **Discord Integration**: discord.py
- **Created by**: Dee
- **Version**: 4.2 with Voice System
