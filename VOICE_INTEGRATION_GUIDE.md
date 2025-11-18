# 🎙️ AiD Voice System Integration Guide

## Current Status: ✅ VOICE IS ALREADY INTEGRATED!

Good news! Your voice system is **already working** and integrated into the main bot. Here's what you have:

---

## ✅ What's Already Implemented

### 1. **TTS (Text-to-Speech)** - FULLY WORKING ✅
- **Location**: `voice_handler.py`
- **Engine**: Coqui XTTS v2 with voice cloning
- **Features**:
  - ✅ Voice cloning with 17 reference samples
  - ✅ Configurable parameters (temperature, speed, etc.)
  - ✅ Discord voice channel integration
  - ✅ Emotion-aware voice (lines 390-434 in voice_handler.py)

### 2. **Voice Commands** - WORKING ✅
- **Location**: `auto_response.py` lines 238-304
- **Commands**:
  ```
  "switch to voice"    → Joins your voice channel & speaks
  "back to the chat"   → Leaves voice channel & returns to text
  ```

### 3. **Dual Output Mode** - WORKING ✅
- **Location**: `auto_response.py` lines 675-703
- When in voice mode, AiD **speaks AND types** every response
- Text is also sent for reference

### 4. **Voice Configuration** - WORKING ✅
- **Location**: `voice_config.py`
- Current config: **Accent Emphasis** (optimized for strong accent)
- Tuning tool: `tune_accent.py` (for finding perfect settings)

---

## ⚠️ What's NOT Yet Implemented

### 1. **STT (Speech-to-Text)** - PARTIALLY IMPLEMENTED ⚠️

**Status**: Code exists but is NOT actively used

**What exists**:
- `voice_handler.py` lines 120-132: STT initialization
- `voice_handler.py` lines 240-282: `listen()` function
- Uses Google Speech Recognition

**What's missing**:
- No active listening loop
- No Discord integration for listening to user voice
- No command to trigger listening

**Why it's not active**:
- Discord bots require **FFmpeg** and **PyNaCl** to receive audio from voice channels
- Requires continuous audio stream processing
- More complex than TTS (needs wake word detection or push-to-talk)

### 2. **Discord Voice Commands** - MISSING ⚠️

No explicit bot commands like `!join`, `!leave`, `!speak`.
Currently relies on text phrases "switch to voice" and "back to the chat".

### 3. **Emotion-Voice Integration** - PARTIAL ⚠️

**What exists**:
- `voice_handler.py` lines 390-434: `speak_with_emotion()` function
- `emotion_voice_mapper.py`: Maps emotions to voice parameters

**What's missing**:
- Not automatically applied in main chat flow
- Emotion detection happens but doesn't adjust voice parameters

---

## 🎯 Next Steps: After Finding Perfect Voice

Once you've found AiD's perfect voice using `tune_accent.py`, here's what to do:

### **Step 1: Apply Your Tuned Settings** ✅

After running `tune_accent.py`:

1. The script will offer to **auto-apply** to `voice_config.py`
2. Or manually copy from `accent_samples/best_config.py`
3. Restart bot to use new settings

### **Step 2: Test Voice Integration** ✅

Test the existing features:

```
You: "switch to voice"
  → AiD joins your voice channel
  → AiD speaks: "Alright boss, I'm in the voice channel now!"

You: (type in text chat) "Hello AiD, how are you?"
  → AiD speaks AND types the response

You: "back to the chat"
  → AiD speaks goodbye
  → AiD leaves voice channel
```

### **Step 3: Add Discord Command Shortcuts** (OPTIONAL)

If you want cleaner commands, add these to `bot.py`:

```python
@bot.command(name='join')
async def join_voice(ctx):
    """Join voice channel."""
    voice_mgr = voice_handler.get_voice()
    if voice_mgr:
        success = await voice_mgr.join_voice_channel(ctx.message)
        if not success:
            await ctx.send("Couldn't join voice channel, mate.")
    else:
        await ctx.send("Voice system not ready.")

@bot.command(name='leave')
async def leave_voice(ctx):
    """Leave voice channel."""
    voice_mgr = voice_handler.get_voice()
    if voice_mgr and voice_mgr.is_in_voice:
        await voice_mgr.speak_in_voice("Alright, heading out!")
        await asyncio.sleep(2)
        await voice_mgr.leave_voice_channel()
        await ctx.send("Left voice channel.")
    else:
        await ctx.send("Not in a voice channel, boss.")
```

---

## 🔧 STT Implementation Verification

### **Current STT Status**: ⚠️ Code exists but NOT integrated

**To verify if STT works** (for local testing, not Discord):

```python
# Test script: test_stt.py
from voice_handler import VoiceHandler

voice = VoiceHandler()

if voice.stt_enabled:
    print("STT is available!")
    print("Speak something...")
    text = voice.listen(timeout=10)
    if text:
        print(f"You said: {text}")
    else:
        print("No speech detected")
else:
    print("STT not available - install: pip install SpeechRecognition pyaudio")
```

### **Why STT Isn't Used in Discord**:

1. **Technical complexity**: Discord voice receiving requires:
   ```bash
   pip install discord.py[voice]
   pip install PyNaCl
   apt-get install ffmpeg  # Linux
   ```

2. **Continuous listening**: Requires audio stream processing:
   ```python
   # This is complex and not yet implemented
   async def listen_in_voice_channel():
       # Receive audio packets from Discord
       # Convert to text using STT
       # Process as message
       # Respond in voice
   ```

3. **Activation method needed**:
   - Wake word ("Hey AiD") - requires custom training
   - Push-to-talk - requires user interaction
   - Continuous - very resource intensive

### **STT Implementation Recommendation**:

**For now**: Focus on TTS (speaking). STT in Discord is complex.

**If you want STT later**:
- Use **push-to-talk** model (user presses button to activate)
- Or use **local microphone** for testing (not Discord)

---

## 🎨 Emotion-Voice Integration

### **How to Enable** (already mostly there):

The code exists in `voice_handler.py` but needs to be called from `auto_response.py`.

**What to change** in `auto_response.py` around line 690:

```python
# BEFORE (current):
if voice_active:
    await voice_mgr.speak_in_voice(chunk)

# AFTER (with emotion):
if voice_active:
    # Get detected emotion from bot.py's emotional_context
    try:
        # You'd need to pass emotion from bot.py's call_aid_api
        # For now, use neutral
        await voice_mgr.speak_in_voice(chunk, emotion="neutral", intensity=0.5)
    except Exception as e:
        # Fallback to no emotion
        await voice_mgr.speak_in_voice(chunk)
```

**Full emotion integration** requires:
1. Passing `emotional_context` from `bot.py` → `auto_response.py`
2. Mapping emotion to voice parameters via `emotion_voice_mapper.py`
3. Restoring voice config after each emotional response

---

## 📋 Summary: What You Have vs What's Missing

| Feature | Status | Location | Notes |
|---------|--------|----------|-------|
| **TTS (Speaking)** | ✅ WORKING | `voice_handler.py` | Fully integrated |
| **Voice Cloning** | ✅ WORKING | 17 samples | Coqui XTTS v2 |
| **Discord Voice** | ✅ WORKING | `auto_response.py` | Join/leave/speak |
| **Voice Config** | ✅ WORKING | `voice_config.py` | Accent emphasis |
| **Tuning Tool** | ✅ COMPLETE | `tune_accent.py` | Interactive tuning |
| **Dual Output** | ✅ WORKING | `auto_response.py` | Voice + text |
| **STT (Listening)** | ⚠️ PARTIAL | `voice_handler.py` | Code exists, not used |
| **Discord STT** | ❌ MISSING | N/A | Complex to implement |
| **Emotion Voice** | ⚠️ PARTIAL | `voice_handler.py` | Exists, not auto-applied |
| **Voice Commands** | ✅ WORKING | Text-based | Could add `!join` `!leave` |

---

## 🚀 Recommended Next Steps (In Order)

### **Priority 1: Perfect the Voice** 🎯
1. Run `python tune_accent.py`
2. Find your favorite accent settings
3. Apply to `voice_config.py`
4. Test with "switch to voice"

### **Priority 2: Test Current Integration** ✅
1. Join a voice channel in Discord
2. Type "switch to voice"
3. Have a conversation (AiD speaks + types)
4. Type "back to the chat" to exit

### **Priority 3: Add Convenience Commands** (Optional)
1. Add `!join` and `!leave` commands to `bot.py`
2. Makes it easier than typing full phrases

### **Priority 4: Enable Emotion-Voice** (Optional)
1. Modify `auto_response.py` to pass emotion to voice
2. Test with different emotional contexts

### **Priority 5: STT Implementation** (Advanced, Optional)
1. Implement push-to-talk Discord listening
2. Or keep STT for local testing only

---

## 🧪 Testing Checklist

Use this to verify everything works:

- [ ] Run `python tune_accent.py` successfully
- [ ] Apply tuned settings to `voice_config.py`
- [ ] Restart bot
- [ ] Join a Discord voice channel
- [ ] Type "switch to voice" in text chat
- [ ] Hear AiD join with greeting
- [ ] Type a message and hear AiD's response
- [ ] Verify AiD's accent is strong and clear
- [ ] Type "back to the chat"
- [ ] Hear AiD say goodbye and leave
- [ ] Confirm all features work smoothly

---

## 🔊 Voice System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     USER INPUT                          │
│  "switch to voice" OR "back to the chat" OR normal msg  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              auto_response.py                           │
│  • Detects voice commands                               │
│  • Routes to voice_handler                              │
│  • Sends dual output (voice + text)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              voice_handler.py                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  VoiceHandler                                    │   │
│  │  • join_voice_channel()                          │   │
│  │  • leave_voice_channel()                         │   │
│  │  • speak_in_voice()                              │   │
│  │  • speak_with_emotion() [optional]               │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  voice_config.py │    │ Coqui XTTS v2    │
│  • TEMPERATURE   │    │ • Voice cloning  │
│  • TOP_P/TOP_K   │    │ • 17 samples     │
│  • SPEED         │    │ • Generation     │
│  • Presets       │    └──────────────────┘
└──────────────────┘
         ▲
         │
         │ (tuning)
         │
┌──────────────────┐
│ tune_accent.py   │
│ • Interactive    │
│ • 3 rounds       │
│ • 5 samples      │
│ • Auto-apply     │
└──────────────────┘
```

---

## ❓ FAQ

### Q: Do I need to reinstall anything?
**A**: No! Voice is already integrated. Just run `tune_accent.py` to find perfect settings.

### Q: Can AiD listen to me speak in Discord?
**A**: Not yet. The code exists for local STT, but Discord voice receiving is complex and not implemented. Focus on TTS for now.

### Q: How do I change reference samples?
**A**: In `voice_config.py`, change `REFERENCE_SAMPLE_INDEX` (0-16 for your 17 samples). Different samples have different accent strengths.

### Q: Why does AiD still type when in voice mode?
**A**: This is intentional! Text acts as a reference and backup. You can modify `auto_response.py` line 698 to disable text output if desired.

### Q: Can I make AiD sound more emotional?
**A**: Yes! The code exists in `emotion_voice_mapper.py`. You need to integrate it into the main flow (see "Emotion-Voice Integration" section above).

### Q: What if the accent is still too weak?
**A**: 1. Try different `REFERENCE_SAMPLE_INDEX` values (0-16)
   2. Run `tune_accent.py` and pick "Ultra Expressive"
   3. Manually push TEMPERATURE to 0.90+ in `voice_config.py`

---

## 📞 Support

If you encounter issues:
1. Check `voice_handler.py` for initialization errors
2. Verify Coqui TTS is installed: `pip install TTS`
3. Ensure Discord voice dependencies: `pip install discord.py[voice]`
4. Check reference samples exist in `voice_samples/reference/`

---

## ✅ Conclusion

**YOU'RE READY!** Your voice system is fully integrated and working. Just:
1. ✅ Run `tune_accent.py` to find perfect accent
2. ✅ Apply settings to `voice_config.py`
3. ✅ Test with "switch to voice"
4. ✅ Enjoy AiD's voice!

The only missing piece is active STT (listening in Discord), which is complex and optional. Focus on perfecting TTS first.

**Happy voicing!** 🎙️
