# AiD Voice System - Quick Start

Get AiD speaking in Discord with emotion-aware voice in 5 steps!

---

## Step 1: Install Dependencies (5 minutes)

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install packages
pip install TTS==0.22.0 transformers==4.33.0
pip install discord.py[voice] sounddevice soundfile

# Install FFmpeg (Windows)
# Download from: https://www.gyan.dev/ffmpeg/builds/
# Extract to C:\ffmpeg
# Add C:\ffmpeg\bin to PATH
```

**Verify:**
```powershell
python test_voice_cloning.py
```

Should show: `✅ Voice cloning is active!`

---

## Step 2: Upload Voice Samples (10 minutes)

Your 17 samples are already in `voice_samples/reference/` ✅

**Check quality:**
```powershell
python check_voice_samples.py
```

Target: 80+ score for each sample

---

## Step 3: Tune Voice Parameters (10 minutes)

```powershell
# Test all presets
python test_voice_tuning.py all

# Listen to 4 generated files:
# - test_clear_and_stable.wav
# - test_natural_and_expressive.wav
# - test_fast_paced.wav
# - test_slow_and_deliberate.wav
```

**Pick your favorite and apply it:**

Edit `voice_config.py`, add at bottom:
```python
# Apply your chosen preset
VoiceConfig.preset_clear_and_stable()  # Or your choice
```

---

## Step 4: Map Emotions to Samples (15 minutes)

1. **Listen to your 17 samples** - note which sound happy, sad, neutral, etc.

2. **Edit `emotion_voice_mapper.py`** - update EMOTION_SAMPLE_MAP:

```python
EMOTION_SAMPLE_MAP = {
    "happy": [0, 1],      # Your happy-sounding samples
    "sad": [2, 3],        # Your sad-sounding samples
    "neutral": [4, 5, 6], # Your neutral samples
    # ... etc
}
```

**Example for your 17 samples:**
- Listen to "AiD Voice Sample 1(2).wav" (sample 0)
- Does it sound happy, sad, neutral, excited?
- Map it to the appropriate emotion

---

## Step 5: Test in Discord (5 minutes)

```powershell
# Start bot
python bot.py
```

**In Discord:**

1. Join a voice channel
2. Type: `switch to voice`
3. AiD joins and speaks!
4. Talk to her (text or voice)
5. She responds with emotion-appropriate voice
6. Type: `back to the chat` to end

**Done!** 🎉

---

## Common Issues

### "TTS not available"
```powershell
pip install TTS==0.22.0 transformers==4.33.0
```

### "FFmpeg not found"
1. Download: https://www.gyan.dev/ffmpeg/builds/
2. Add to PATH
3. Restart terminal

### Voice is slurred
```python
# In voice_config.py
VoiceConfig.preset_clear_and_stable()
```

### Pauses too long
```python
# In voice_config.py
VoiceConfig.preset_fast_paced()
```

---

## What's Next?

- Read `VOICE_TUNING_GUIDE.md` for parameter details
- Read `VOICE_INTEGRATION_GUIDE.md` for full setup
- Customize emotion presets in `emotion_voice_mapper.py`
- Fine-tune parameters in `voice_config.py`

---

## File Structure

```
AiD/
├── voice_samples/
│   └── reference/          # Your 17 voice samples ✅
├── voice_handler.py        # Main voice system
├── voice_config.py         # Voice parameters (tune here)
├── emotion_voice_mapper.py # Emotion → voice mapping
├── test_voice_cloning.py   # Test voice cloning
├── test_voice_tuning.py    # Test parameters
├── check_voice_samples.py  # Verify sample quality
├── QUICK_START.md          # This file
├── VOICE_TUNING_GUIDE.md   # Parameter tuning guide
└── VOICE_INTEGRATION_GUIDE.md  # Complete setup guide
```

---

## Usage

**In Discord:**
- `switch to voice` - AiD joins voice channel
- `back to the chat` - AiD leaves voice channel

**In Code:**
```python
from voice_handler import get_voice

voice = get_voice()

# Speak with emotion
await voice.speak_in_voice("Hello!", emotion="happy", intensity=0.8)
```

---

**Total setup time: ~45 minutes**

**Result: AiD speaking in Discord with emotion-aware, GPT-SoVITS-cloned voice!**
