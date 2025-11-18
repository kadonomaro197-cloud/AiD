# 🎯 AiD Voice System - Quick Start

## ✅ Your Voice System is READY TO USE!

### **Step 1: Find Perfect Voice Settings**
```bash
python tune_accent.py
```
- Generates 5 samples at a time
- Pick your favorite
- Repeats 3 rounds to refine
- Auto-applies best settings

### **Step 2: Test Voice in Discord**
```
1. Join any voice channel in Discord
2. Type: "switch to voice"
3. AiD joins and speaks!
4. Type any message → AiD speaks AND types
5. Type: "back to the chat" when done
```

---

## 🎙️ Current Voice Commands

| Command | What It Does |
|---------|--------------|
| `"switch to voice"` | AiD joins your voice channel & starts speaking |
| `"back to the chat"` | AiD leaves voice channel & returns to text-only |
| *(normal chat)* | If in voice mode: AiD speaks + types every response |

---

## ⚙️ Voice Configuration Files

| File | Purpose |
|------|---------|
| `voice_config.py` | **Main settings** - temperature, speed, accent strength |
| `tune_accent.py` | **Interactive tuner** - finds perfect accent settings |
| `voice_handler.py` | **Engine** - handles TTS, Discord voice, emotions |
| `voice_samples/reference/` | **Your 17 voice samples** - voice cloning source |
| `accent_samples/` | **Tuning results** - saved samples + best config |

---

## 🔧 Manual Voice Tweaks

### **Make Accent STRONGER**:
Edit `voice_config.py`:
```python
TEMPERATURE = 0.88          # Higher = more expressive (was 0.82)
REPETITION_PENALTY = 1.5    # Lower = more accent patterns (was 1.8)
TOP_P = 0.96                # Higher = more diversity (was 0.94)
```

### **Make Accent CLEARER**:
```python
TEMPERATURE = 0.65          # Lower = more consistent
REPETITION_PENALTY = 3.0    # Higher = less repetition
TOP_P = 0.85                # Lower = more focused
```

### **Try Different Voice Sample**:
```python
REFERENCE_SAMPLE_INDEX = 5  # Try 0-16 (you have 17 samples)
```

---

## ❌ STT (Speech-to-Text) Status

**Question**: "Can AiD listen to me speak?"

**Answer**: Not in Discord (yet). Here's why:

| Feature | Status | Notes |
|---------|--------|-------|
| **Local STT** | ✅ Works | `voice.listen()` - microphone input |
| **Discord STT** | ❌ Not implemented | Complex - needs audio stream processing |

**STT Code exists but isn't actively used in Discord bot.**

To test local STT (not Discord):
```python
from voice_handler import VoiceHandler
voice = VoiceHandler()
text = voice.listen(timeout=10)  # Speak into mic
print(f"You said: {text}")
```

**Discord STT is complex** - requires:
- FFmpeg, PyNaCl
- Continuous audio stream handling
- Wake word OR push-to-talk system
- High CPU/bandwidth usage

**Recommendation**: Focus on perfecting TTS first.

---

## 🎨 Emotion-Aware Voice (Optional)

**Status**: Code exists but not auto-enabled

**To enable emotion in voice**:
1. AiD already detects emotions in `bot.py`
2. `emotion_voice_mapper.py` can adjust voice for emotions
3. Not automatically applied yet

**Manual test**:
```python
from voice_handler import VoiceHandler
voice = VoiceHandler()

# Speak with specific emotion
voice.speak_with_emotion(
    "I'm feeling quite happy today!",
    emotion="joy",
    intensity=0.7
)
```

---

## 🐛 Troubleshooting

### "Voice handler not ready"
```bash
pip install TTS sounddevice soundfile
```

### "Can't join voice channel"
```bash
pip install discord.py[voice] PyNaCl
# Linux: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
# Windows: Download ffmpeg and add to PATH
```

### "Accent too weak"
1. Try different `REFERENCE_SAMPLE_INDEX` (0-16)
2. Run `tune_accent.py` and pick "Ultra Expressive"
3. Increase `TEMPERATURE` to 0.88-0.92

### "Speech sounds garbled"
1. Lower `TEMPERATURE` (try 0.65-0.75)
2. Increase `REPETITION_PENALTY` (try 3.0-4.0)
3. Check reference samples quality

---

## 📊 What's Working vs Missing

### ✅ **WORKING** (Ready to use now):
- [x] TTS (Text-to-Speech)
- [x] Voice cloning with your 17 samples
- [x] Discord voice channel integration
- [x] Voice commands ("switch to voice", "back to chat")
- [x] Dual output (speaks + types)
- [x] Configurable voice parameters
- [x] Interactive accent tuning tool

### ⚠️ **PARTIAL** (Code exists, not integrated):
- [ ] STT (Speech-to-Text) - local only
- [ ] Emotion-aware voice - needs connection
- [ ] Discord bot commands (!join, !leave)

### ❌ **MISSING** (Not implemented):
- [ ] Discord STT (listening in voice channel)
- [ ] Wake word detection
- [ ] Voice activity detection (VAD)

---

## 🎯 Recommended Workflow

```
┌─────────────────────────────────────────┐
│  1. Run tune_accent.py                  │
│     → Find perfect accent settings      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Settings auto-applied to            │
│     voice_config.py                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Restart bot                         │
│     → New voice settings active         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. Test in Discord:                    │
│     • "switch to voice"                 │
│     • Chat normally                     │
│     • "back to the chat"                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  5. Fine-tune if needed:                │
│     • Try different REFERENCE_SAMPLE_INDEX │
│     • Adjust TEMPERATURE manually       │
│     • Re-run tune_accent.py             │
└─────────────────────────────────────────┘
```

---

## 📝 Summary

**YOU'RE ALL SET!**

Your voice system is:
- ✅ Fully integrated with Discord
- ✅ Using Coqui XTTS v2 voice cloning
- ✅ Configured for strong accent
- ✅ Ready to use RIGHT NOW

**Just run** `python tune_accent.py` to find your favorite settings, then test with `"switch to voice"` in Discord!

**STT (listening) is optional** and complex - focus on speaking first.

---

**Need help?** Check `VOICE_INTEGRATION_GUIDE.md` for detailed technical info.

**Happy voicing!** 🎙️🎉
