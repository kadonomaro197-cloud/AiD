# AiD Voice Tuning Guide

Complete guide for adjusting AiD's voice parameters to get perfect speech quality.

## Quick Start

### 1. Test All Presets (Recommended First Step)

```powershell
python test_voice_tuning.py all
```

This generates 4 test files with different settings:
- `test_clear_and_stable.wav` - Clear, minimal slurring
- `test_natural_and_expressive.wav` - More natural, expressive
- `test_fast_paced.wav` - Faster speech, shorter pauses
- `test_slow_and_deliberate.wav` - Slower, more thoughtful

**Listen to all 4 files and pick your favorite!**

### 2. Apply Your Favorite Preset

Edit `voice_config.py` and add this near the bottom:

```python
# Apply preset at module load
VoiceConfig.preset_clear_and_stable()  # Or whichever you prefer
```

### 3. Test Your Changes

```powershell
python test_voice_cloning.py
```

---

## Manual Tuning

If none of the presets are perfect, you can manually adjust parameters in `voice_config.py`:

### Key Parameters

#### **TEMPERATURE** (Controls clarity vs expressiveness)
- `0.1-0.5`: Very consistent, clearer, less slurring ✅ **Start here if speech is slurred**
- `0.5-0.7`: Balanced (RECOMMENDED)
- `0.7-1.0`: More expressive but may vary

**Fix slurring:** Set to `0.45-0.55`

#### **REPETITION_PENALTY** (Reduces repetitive sounds)
- `1.0-2.0`: May repeat sounds/words
- `2.0-5.0`: Balanced (RECOMMENDED)
- `5.0-10.0`: Aggressively avoids repetition

**Fix repetition:** Increase to `4.0-6.0`

#### **LENGTH_PENALTY** (Controls pacing and pauses)
- `0.5-0.9`: Faster, shorter pauses ✅ **Start here if pauses too long**
- `1.0`: Natural pacing
- `1.0-2.0`: Slower, longer pauses

**Fix long pauses:** Set to `0.7-0.9`

#### **TOP_K** (Vocabulary selection)
- `10-30`: More predictable, clearer
- `50`: Balanced (RECOMMENDED)
- `100+`: More varied

#### **TOP_P** (Probability threshold)
- `0.7-0.85`: More focused, clearer
- `0.85-0.9`: Balanced (RECOMMENDED)
- `0.9-1.0`: More creative

#### **ENABLE_TEXT_SPLITTING**
- `True`: Better for long text, natural sentence pauses
- `False`: Better for short phrases ✅ **Set to False if pauses too long**

#### **SPEED**
- `0.5-0.9`: Slower
- `1.0`: Normal
- `1.1-1.5`: Faster

**Note:** Not all XTTS versions support the speed parameter.

#### **REFERENCE_SAMPLE_INDEX**
- `0-16`: Use specific sample (you have 17 samples)
- `-1`: Random sample each time
- Try different samples - each has different emotional tone!

---

## Testing Workflow

### Test Current Settings
```powershell
python test_voice_tuning.py
```
Generates: `test_current_config.wav`

### Test Specific Preset
```powershell
python test_voice_tuning.py clear     # Clear and Stable
python test_voice_tuning.py natural   # Natural and Expressive
python test_voice_tuning.py fast      # Fast Paced
python test_voice_tuning.py slow      # Slow and Deliberate
```

### Test Custom Phrase
```powershell
python test_voice_tuning.py "Your custom text here"
```
Generates: `test_custom_phrase.wav`

---

## Common Problems & Solutions

### Problem: Speech sounds slurred or mumbly
**Quick Fix:**
```powershell
python test_voice_tuning.py clear
```
Or manually edit `voice_config.py`:
```python
TEMPERATURE = 0.45
REPETITION_PENALTY = 4.0
TOP_P = 0.80
```

### Problem: Pauses are too long
**Quick Fix:**
```powershell
python test_voice_tuning.py fast
```
Or manually edit `voice_config.py`:
```python
LENGTH_PENALTY = 0.8
ENABLE_TEXT_SPLITTING = False
```

### Problem: Speech sounds robotic
**Quick Fix:**
```powershell
python test_voice_tuning.py natural
```
Or manually edit `voice_config.py`:
```python
TEMPERATURE = 0.75
REPETITION_PENALTY = 2.0
TOP_P = 0.90
```

### Problem: Words or sounds repeat
**Solution:**
```python
REPETITION_PENALTY = 5.0
TEMPERATURE = 0.55
```

### Problem: Voice doesn't match samples well
**Solutions:**
1. Check sample quality:
   ```powershell
   python check_voice_samples.py
   ```
2. Try different reference samples:
   ```python
   REFERENCE_SAMPLE_INDEX = 1  # Try samples 0-16
   ```
3. Verify samples are:
   - 10-20 seconds long
   - Clean audio (no background noise)
   - Mono, 22050 Hz or 44100 Hz
   - Same speaker throughout

---

## Advanced: Sample-Specific Tuning

Since you have 17 different voice samples, you can:

1. **Listen to your samples** and identify which emotional tones they have
2. **Map them** in `voice_config.py`:
   ```python
   # Sample 0-2: Neutral/conversational
   # Sample 3-4: Happy/excited
   # Sample 5-6: Calm/gentle
   # etc.
   ```
3. **Choose the appropriate sample** for different contexts:
   ```python
   REFERENCE_SAMPLE_INDEX = 3  # Use happy sample
   ```

Or use `-1` for random selection to get variety!

---

## Integration with Discord Bot

Once you're happy with your settings, AiD will automatically use them when speaking in Discord!

The voice is used in:
- `bot.py` - Main bot voice interactions
- `auto_response.py` - Voice commands ("switch to voice", "back to the chat")

---

## Files Overview

- **`voice_config.py`** - All tunable parameters and presets
- **`voice_handler.py`** - Voice system (uses voice_config.py)
- **`test_voice_tuning.py`** - Test different configurations
- **`test_voice_cloning.py`** - Full system test
- **`check_voice_samples.py`** - Analyze sample quality

---

## Recommended Workflow

1. **Start:** Test all presets → `python test_voice_tuning.py all`
2. **Listen:** Compare the 4 generated files
3. **Pick:** Choose closest preset
4. **Refine:** Adjust 1-2 parameters in `voice_config.py`
5. **Test:** `python test_voice_tuning.py`
6. **Repeat 4-5** until perfect
7. **Deploy:** Run Discord bot with new voice!

---

## Tips for Best Results

✅ **DO:**
- Start with presets, then fine-tune
- Change one parameter at a time
- Test after each change
- Use high-quality voice samples (check with `check_voice_samples.py`)

❌ **DON'T:**
- Change multiple parameters at once
- Use extreme values (e.g., TEMPERATURE = 0.1 or 1.0)
- Skip testing before deploying to Discord
- Use low-quality or noisy voice samples

---

## Need Help?

Check the detailed comments in `voice_config.py` for parameter explanations and the troubleshooting guide at the bottom of that file.
