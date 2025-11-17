# AiD Voice Integration - Complete Setup Guide

Complete guide to integrating GPT-SoVITS voice samples with AiD's emotion-aware Discord voice system.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Voice Sample Setup](#voice-sample-setup)
4. [Emotion-Sample Mapping](#emotion-sample-mapping)
5. [Testing Voice System](#testing-voice-system)
6. [Discord Integration](#discord-integration)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.9-3.11 (Python 3.12+ not yet supported by TTS)
- FFmpeg (for Discord voice)
- Virtual environment (recommended)

### Required Packages
```powershell
pip install discord.py[voice]
pip install TTS==0.22.0
pip install transformers==4.33.0
pip install sounddevice soundfile
pip install pyttsx3
```

### FFmpeg Installation (Windows)
1. Download FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH
4. Verify: `ffmpeg -version`

---

## Installation

### Step 1: Install Dependencies

```powershell
# Activate your venv
.\venv\Scripts\Activate.ps1

# Install core packages
pip install discord.py[voice]
pip install TTS==0.22.0
pip install transformers==4.33.0
pip install sounddevice soundfile pyttsx3
```

### Step 2: Verify Installation

```powershell
python -c "from TTS.api import TTS; print('TTS OK')"
python -c "import discord; print('Discord OK')"
python -c "import sounddevice; print('Audio OK')"
ffmpeg -version
```

All should complete without errors.

---

## Voice Sample Setup

### Step 1: Create Directory Structure

```powershell
mkdir voice_samples\reference
```

### Step 2: Generate Samples with GPT-SoVITS

**Recommended Samples:**
- **5-10 total samples**
- **10-20 seconds each**
- **Varied emotions:**
  - 2-3 neutral/conversational
  - 1-2 happy/excited
  - 1-2 calm/gentle
  - 1 sad/contemplative
  - 1 determined/confident

**Technical Requirements:**
- Format: WAV (preferred), MP3, FLAC, or OGG
- Sample Rate: 22050 Hz or 44100 Hz
- Channels: Mono (stereo will be converted)
- Bit Depth: 16-bit or 32-bit
- Clean audio, no background noise

### Step 3: Name and Upload Samples

**Example naming:**
```
voice_samples/reference/
  ├── neutral_01.wav
  ├── neutral_02.wav
  ├── happy_01.wav
  ├── calm_01.wav
  ├── sad_01.wav
  └── confident_01.wav
```

Or use your current naming:
```
voice_samples/reference/
  ├── AiD Voice Sample 1(2).wav
  ├── AiD Voice Sample 2(1).wav
  └── ...
```

### Step 4: Verify Sample Quality

```powershell
python check_voice_samples.py
```

**Target:** Quality score of 80+ for each sample

**If score is low:**
- Check duration (10-20 seconds)
- Verify sample rate (22050 or 44100 Hz)
- Convert to mono if stereo
- Remove background noise
- Ensure adequate volume (not too quiet)

---

## Emotion-Sample Mapping

### Step 1: Listen to Your Samples

Play each sample and note its emotional tone.

### Step 2: Map Emotions to Sample Indices

Edit `emotion_voice_mapper.py` and update the `EMOTION_SAMPLE_MAP`:

```python
EMOTION_SAMPLE_MAP = {
    # Map based on YOUR specific samples (0-16 for your 17 samples)
    "joy": [0, 1],           # Samples 0-1 sound happy
    "happy": [0, 1],
    "excitement": [2, 3],    # Samples 2-3 sound excited
    "excited": [2, 3],
    "neutral": [4, 5, 6],    # Samples 4-6 are conversational
    "sad": [7, 8],           # Samples 7-8 sound sad
    "sadness": [7, 8],
    "angry": [9, 10],        # Samples 9-10 sound angry/intense
    "anger": [9, 10],
    "frustrated": [11, 12],
    "frustration": [11, 12],
    "anxious": [13, 14],
    "anxiety": [13, 14],
    "curious": [15, 16],
    "confused": [15, 16],
    "playful": [0, 1, 2],
    "pride": [4, 5],
}
```

**Example mapping for your 17 samples:**
```python
# Listen to each sample and categorize by emotion
# Sample 0 (AiD Voice Sample 1(2).wav): Happy, upbeat
# Sample 1 (AiD Voice Sample 2(1).wav): Happy, warm
# Sample 2 (AiD Voice Sample 2(2).wav): Excited
# ... etc
```

### Step 3: Test Emotion Mapping

```powershell
python test_voice_tuning.py
```

The system will randomly select samples based on your mapping.

---

## Testing Voice System

### Test 1: Basic Voice Cloning

```powershell
python test_voice_cloning.py
```

**Expected output:**
```
✅ Voice cloning is active!
TTS Mode: coqui
Voice Cloning: True
Reference Samples: 17
```

### Test 2: Voice Parameter Presets

```powershell
python test_voice_tuning.py all
```

This generates 4 test files with different voice characteristics:
- `test_clear_and_stable.wav`
- `test_natural_and_expressive.wav`
- `test_fast_paced.wav`
- `test_slow_and_deliberate.wav`

**Listen and choose your favorite!**

### Test 3: Emotion-Based Voice

Create `test_emotions.py`:
```python
from voice_handler import get_voice

voice = get_voice()

# Test different emotions
emotions = ["happy", "sad", "excited", "neutral", "angry"]

for emotion in emotions:
    print(f"\nTesting emotion: {emotion}")
    output_file = f"test_emotion_{emotion}.wav"
    voice.speak_with_emotion(
        text=f"This is AiD speaking with {emotion} emotion.",
        emotion=emotion,
        intensity=0.7,
        output_file=output_file
    )
    print(f"Saved to: {output_file}")
```

Run it:
```powershell
python test_emotions.py
```

**Listen to each emotion file** to verify the voice changes appropriately.

---

## Discord Integration

### Step 1: Enable Discord Voice Intents

Edit your Discord bot application settings:
1. Go to https://discord.com/developers/applications
2. Select your bot
3. Go to "Bot" → "Privileged Gateway Intents"
4. Enable:
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
   - ✅ VOICE STATE INTENT (if available)

### Step 2: Verify bot.py has Correct Intents

Check `bot.py` has:
```python
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True  # Important for voice

client = discord.Client(intents=intents)
```

### Step 3: Test Discord Commands

**Start your bot:**
```powershell
python bot.py
```

**In Discord:**

1. **Join a voice channel**

2. **Send:** `switch to voice`
   - AiD should join your voice channel
   - You'll hear her say: "Alright boss, I'm in the voice channel now!"

3. **Talk to AiD** (text or voice if STT enabled)
   - She'll respond in voice with emotion-appropriate parameters

4. **Send:** `back to the chat`
   - AiD will say goodbye and leave the channel

---

## Usage Examples

### Example 1: Manual Emotion Control

In `bot.py` or custom script:

```python
from voice_handler import get_voice
from emotion_voice_mapper import set_voice_for_emotion

# Detect or determine emotion
emotion = "happy"
intensity = 0.8

# Apply emotion to voice
set_voice_for_emotion(emotion, intensity)

# Speak with that emotion
voice = get_voice()
await voice.speak_in_voice("I'm so glad to see you!", emotion=emotion, intensity=intensity)
```

### Example 2: Auto-Detect Emotion from Text

```python
from voice_handler import get_voice
from emotion_voice_mapper import get_emotion_from_text

user_message = "I'm so excited about this new feature!"

# Auto-detect emotion
emotion, intensity = get_emotion_from_text(user_message)

# Generate response with matching emotion
response = "I'm excited too! This is going to be amazing!"

voice = get_voice()
await voice.speak_in_voice(response, emotion=emotion, intensity=intensity)
```

### Example 3: Integration with Emotion Intelligence

```python
from voice_handler import get_voice
from emotion_intelligence import EmotionDetector
from emotion_voice_mapper import set_voice_for_emotion

# Detect emotion from user message
detector = EmotionDetector()
emotion_data = detector.detect(user_message)

if emotion_data:
    top_emotion = emotion_data[0]
    emotion_name = top_emotion["emotion"]
    intensity = top_emotion["intensity"]

    # Generate AiD's response (from your LLM)
    aid_response = "..."

    # Speak with detected emotion
    voice = get_voice()
    await voice.speak_in_voice(aid_response, emotion=emotion_name, intensity=intensity)
```

### Example 4: Context-Aware Voice

```python
from emotion_voice_mapper import EmotionVoiceMapper

# For explanations: slower, clearer
EmotionVoiceMapper.apply_context("explanation")
await voice.speak_in_voice("Let me explain how this works...")

# For greetings: faster, upbeat
EmotionVoiceMapper.apply_context("greeting")
await voice.speak_in_voice("Hey there! Good to see you!")

# Combined emotion + context
EmotionVoiceMapper.apply_combined("happy", intensity=0.7, context="greeting")
await voice.speak_in_voice("Hello! I'm so happy you're here!")
```

---

## Full Integration into bot.py

### Step 1: Add Emotion Detection to Responses

Edit `bot.py` or your message handler:

```python
import voice_handler
from emotion_intelligence import EmotionDetector
from emotion_voice_mapper import set_voice_for_emotion

detector = EmotionDetector()

async def on_message(message):
    # ... your existing code ...

    # Detect emotion from user message
    emotion_data = detector.detect(message.content)
    emotion = "neutral"
    intensity = 0.5

    if emotion_data and len(emotion_data) > 0:
        emotion = emotion_data[0]["emotion"]
        intensity = emotion_data[0]["intensity"]

    # Generate response (your existing LLM call)
    aid_response = await call_aid_api(message.content)

    # Get voice handler
    voice = voice_handler.get_voice()

    # If in voice channel, speak with emotion
    if voice.is_in_voice:
        await voice.speak_in_voice(aid_response, emotion=emotion, intensity=intensity)

    # Always send text response too
    await message.channel.send(aid_response)
```

### Step 2: Add Voice Commands

The commands are already in `auto_response.py` (lines 240-299):
- `switch to voice` - Join voice channel
- `back to the chat` - Leave voice channel

These should work automatically if you have `auto_response.py` integrated.

### Step 3: Optional: Add Voice Toggle Command

Add a command to enable/disable voice responses:

```python
voice_enabled = True

if message.content.lower() == "voice on":
    voice_enabled = True
    await message.channel.send("Voice responses enabled!")

if message.content.lower() == "voice off":
    voice_enabled = False
    await message.channel.send("Voice responses disabled. Text only mode.")
```

---

## Troubleshooting

### Problem: "TTS not available (install TTS)"

**Solution:**
```powershell
pip install TTS==0.22.0 transformers==4.33.0
python -c "from TTS.api import TTS; print('OK')"
```

### Problem: "ImportError: cannot import name 'BeamSearchScorer'"

**Solution:**
```powershell
pip install transformers==4.33.0
```

### Problem: "FFmpeg not found"

**Solution:**
1. Download FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. Add to PATH
3. Restart terminal
4. Verify: `ffmpeg -version`

### Problem: Voice is slurred or unclear

**Solution:**
1. Edit `voice_config.py`:
   ```python
   TEMPERATURE = 0.45  # Lower = clearer
   REPETITION_PENALTY = 4.0  # Higher = less repetition
   ```
2. Or use preset:
   ```python
   VoiceConfig.preset_clear_and_stable()
   ```

### Problem: Pauses are too long

**Solution:**
1. Edit `voice_config.py`:
   ```python
   LENGTH_PENALTY = 0.8  # Lower = shorter pauses
   ENABLE_TEXT_SPLITTING = False
   ```
2. Or use preset:
   ```python
   VoiceConfig.preset_fast_paced()
   ```

### Problem: Voice doesn't match samples

**Solution:**
1. Check sample quality:
   ```powershell
   python check_voice_samples.py
   ```
2. Ensure samples are:
   - 10-20 seconds long
   - Clean audio (no noise)
   - Mono, 22050/44100 Hz
   - Same speaker
3. Try different sample index:
   ```python
   VoiceConfig.REFERENCE_SAMPLE_INDEX = 3  # Try different samples
   ```

### Problem: Discord voice doesn't work

**Solutions:**
- Check bot has voice permissions in Discord server
- Verify FFmpeg is installed and in PATH
- Enable voice_states intent in Discord developer portal
- Check you're in a voice channel when using "switch to voice"
- Look for errors in console

### Problem: Emotions don't change voice

**Solutions:**
1. Verify emotion_voice_mapper.py is imported
2. Check emotion name spelling (use lowercase)
3. Verify EMOTION_SAMPLE_MAP has your emotion listed
4. Test manually:
   ```python
   from emotion_voice_mapper import set_voice_for_emotion
   set_voice_for_emotion("happy", 0.8)
   ```

---

## Advanced Configuration

### Custom Emotion Parameters

Edit `emotion_voice_mapper.py` to create custom emotion presets:

```python
EMOTION_PRESETS = {
    "my_custom_emotion": {
        "temperature": 0.70,
        "repetition_penalty": 2.5,
        "length_penalty": 1.0,
        "top_k": 60,
        "top_p": 0.86,
        "speed": 1.05,
        "enable_text_splitting": True,
        "description": "Custom emotion description"
    },
}
```

### Dynamic Sample Selection

Use different samples based on time of day or context:

```python
import datetime

hour = datetime.datetime.now().hour

if hour < 12:
    # Morning: use energetic samples
    VoiceConfig.REFERENCE_SAMPLE_INDEX = 2
elif hour < 18:
    # Afternoon: use neutral samples
    VoiceConfig.REFERENCE_SAMPLE_INDEX = 5
else:
    # Evening: use calm samples
    VoiceConfig.REFERENCE_SAMPLE_INDEX = 7
```

---

## Summary Checklist

Setup complete when you can check all these:

- ✅ TTS installed and working (`python test_voice_cloning.py`)
- ✅ FFmpeg installed (`ffmpeg -version`)
- ✅ 5-10 voice samples in `voice_samples/reference/`
- ✅ Samples quality score 80+ (`python check_voice_samples.py`)
- ✅ Emotion mapping configured (`emotion_voice_mapper.py`)
- ✅ Voice parameters tuned (`voice_config.py`)
- ✅ Discord voice commands work (`switch to voice`)
- ✅ Emotion affects voice characteristics (test with `test_emotions.py`)
- ✅ AiD speaks in Discord voice channel with appropriate emotion

**You're ready to go!** AiD can now speak in Discord with emotion-aware, GPT-SoVITS-cloned voice that adapts to context and mood!

---

## Files Reference

| File | Purpose |
|------|---------|
| `voice_handler.py` | Main voice system, Discord integration |
| `voice_config.py` | Voice parameters and presets |
| `emotion_voice_mapper.py` | Emotion → voice parameter mapping |
| `test_voice_cloning.py` | Test basic voice cloning |
| `test_voice_tuning.py` | Test parameter presets |
| `check_voice_samples.py` | Verify sample quality |
| `VOICE_TUNING_GUIDE.md` | Parameter tuning documentation |
| `VOICE_INTEGRATION_GUIDE.md` | This file - complete setup |

---

## Next Steps

1. **Fine-tune voice parameters** based on your preferences
2. **Test in Discord** with real conversations
3. **Adjust emotion mappings** based on how they sound
4. **Customize sample selection** for different contexts
5. **Enjoy AiD's expressive voice!**

---

Need help? Check the troubleshooting section or review the individual guide files.
