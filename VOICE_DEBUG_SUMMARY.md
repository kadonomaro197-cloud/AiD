# Voice Testing vs Discord Operation - Debug Summary

## Issues Found and Fixed

### 🔴 Critical Issue #1: Initialization Parameter Mismatch
**Location:** `bot.py:998`

**Problem:**
```python
voice_handler.init_voice(bot)  # ❌ Passing parameter bot doesn't accept
```

**Root Cause:**
- `bot.py` was calling `init_voice(bot)` with a bot parameter
- `voice_handler.py` function signature: `def init_voice():` (no parameters)
- This mismatch would cause initialization to fail silently
- System would fall back to pyttsx3 instead of Coqui TTS

**Fix:** Removed the bot parameter from the call in `bot.py:998`

---

### 🔴 Critical Issue #2: Extreme Voice Configuration
**Location:** `voice_config.py`

**Problem:**
```python
TEMPERATURE = 0.98        # Too high (recommended: 0.65-0.82)
REPETITION_PENALTY = 1.5  # Too low (recommended: 2.5-3.0)
TOP_K = 120               # Too high (recommended: 50-90)
TOP_P = 0.99              # Too high (recommended: 0.85-0.94)
```

**Impact:**
- These extreme settings can cause Coqui TTS to fail during generation
- More likely to timeout or produce corrupted audio
- Discord streaming is more sensitive to these issues than local testing

**Status:** ⚠️ NOT YET FIXED (would you like me to reset to stable values?)

---

### ⚠️ Issue #3: Missing FFmpeg Validation
**Location:** `voice_handler.py` (Discord voice operations)

**Problem:**
- No check if FFmpeg is installed before attempting Discord voice streaming
- Unclear error messages when FFmpeg is missing

**Fix:**
- Added `_check_ffmpeg()` method that validates FFmpeg installation
- Checks both PATH and version on initialization
- Added `ffmpeg_available` status to voice handler
- Early return with clear error if FFmpeg missing

---

## Comprehensive Diagnostics Added

### Initialization Logging
Now shows:
- ✅ FFmpeg path and version
- ✅ Coqui TTS model loading status
- ✅ Reference audio sample paths (all 17 samples)
- ✅ Detailed error traces for initialization failures

### Discord Voice Logging
Now shows:
- ✅ TTS mode (coqui vs pyttsx3)
- ✅ FFmpeg availability status
- ✅ Voice client connection status
- ✅ Emotion parameter application
- ✅ Reference sample selection
- ✅ Voice parameters (temp, top_k, top_p, etc.)
- ✅ Audio generation timing
- ✅ File size validation
- ✅ Playback duration tracking
- ✅ Step-by-step failure points

### Test vs Discord Differences

| Feature | Voice Testing | Discord Operation |
|---------|--------------|-------------------|
| Code Path | `test_voice_cloning.py` → `speak()` | `bot.py` → `speak_in_voice()` |
| Audio Output | Local playback via sounddevice | FFmpeg streaming to Discord |
| Parameters | Direct from voice_config.py | Overridden by emotion_voice_mapper |
| Complexity | Simple (1 step) | Complex (5+ steps) |
| FFmpeg Required | ❌ No | ✅ Yes |
| Temp File | Optional | Required |
| Error Handling | Basic | Now comprehensive |

---

## Next Steps to Debug

When you run your bot next time, look for these log messages:

### 1. FFmpeg Check (on startup)
```
[VOICE DEBUG] Checking FFmpeg availability...
[VOICE DEBUG] FFmpeg found at: /usr/bin/ffmpeg
[VOICE DEBUG] ffmpeg version 4.x.x
[VOICE] ✅ FFmpeg is available for Discord voice streaming
```

**If you see:**
```
[VOICE] ⚠️ FFmpeg NOT available - Discord voice will NOT work
```
→ Install FFmpeg from https://ffmpeg.org/download.html

### 2. Coqui TTS Initialization
```
[VOICE DEBUG] Attempting to initialize Coqui TTS...
[VOICE DEBUG] TTS module imported successfully
[VOICE DEBUG] Found 17 reference samples:
[VOICE DEBUG]   [0] /path/to/sample_0.wav
...
[VOICE DEBUG] Loading XTTS v2 model...
[VOICE DEBUG] XTTS v2 model loaded successfully
[VOICE] ✅ TTS initialized with Coqui TTS (voice cloning)
```

**If you see:**
```
[VOICE ERROR] System is using pyttsx3 fallback instead of Coqui TTS
```
→ This means Coqui TTS failed to initialize (check previous errors)

### 3. Discord Voice Attempt
```
[VOICE DEBUG] Starting speak_in_voice for text: '...'
[VOICE DEBUG] TTS mode: coqui, TTS enabled: True
[VOICE DEBUG] FFmpeg available: True
[VOICE DEBUG] Applying emotion: happy with intensity: 0.80
[VOICE DEBUG] Voice parameters: temp=0.72, rep_pen=2.2, ...
[VOICE DEBUG] Calling Coqui TTS engine...
[VOICE DEBUG] TTS generation completed in 3.45s
[VOICE DEBUG] Output file size: 245678 bytes
[VOICE DEBUG] FFmpeg audio source created successfully
[VOICE DEBUG] Starting audio playback...
[VOICE DEBUG] Playback completed after 5.2s
[VOICE] ✅ Successfully spoke in voice channel
```

**Look for any steps that fail** - the detailed logging will show exactly where the problem occurs.

---

## Common Failure Scenarios

### Scenario 1: "Using pyttsx3 fallback"
**Cause:** Coqui TTS failed to initialize
**Check:**
- Is TTS installed? `pip install TTS`
- Are reference samples in `voice_samples/reference/`?
- Check initialization logs for import errors

### Scenario 2: "FFmpeg may not be installed"
**Cause:** FFmpeg not in PATH
**Fix:**
- Download from https://ffmpeg.org/download.html
- Add to system PATH
- Restart your bot

### Scenario 3: "Failed to generate speech audio file"
**Cause:** Extreme voice parameters causing Coqui TTS to fail
**Check:** Voice parameters in logs - look for values outside recommended ranges
**Fix:** Reset `voice_config.py` to stable values (I can do this for you)

### Scenario 4: "TTS generation completed in 15.3s"
**Cause:** Generation too slow (extreme parameters)
**Impact:** May timeout before streaming starts
**Fix:** Lower TEMPERATURE, TOP_K, TOP_P values

---

## Recommended Actions

1. ✅ **Run your bot and check the logs** - The new diagnostics will tell you exactly what's failing

2. ⚠️ **Consider resetting voice_config.py** - Your current settings are extremely aggressive:
   - Would you like me to reset them to stable values?
   - Or create a new "discord_safe" preset?

3. ✅ **Verify FFmpeg installation** - Make sure it's in your PATH

4. ✅ **Test the emotion override** - The emotion_voice_mapper may be conflicting with your base settings

---

## Files Modified

- ✅ `bot.py` - Fixed init_voice() call, added error trace
- ✅ `voice_handler.py` - Added FFmpeg check, comprehensive logging
- 📝 `voice_config.py` - NOT modified (still has extreme settings)

---

## Testing Recommendations

1. Start bot with voice logging enabled
2. Join a Discord voice channel
3. Trigger AID to speak
4. Review the diagnostic output
5. Share the logs with me if issues persist

The new logging will show exactly where Discord voice is failing compared to your test files!
