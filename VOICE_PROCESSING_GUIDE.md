# Voice Sample Processing Guide

Complete guide for processing voice samples to optimize them for XTTS voice cloning.

## Quick Start

### Method 1: Automated Processing (Recommended)

**Step 1: Enable Audacity Scripting**

1. Open Audacity
2. Go to **Edit → Preferences** (or **Audacity → Preferences** on Mac)
3. Click on **Modules** in the left sidebar
4. Find **mod-script-pipe** in the list
5. Change it from "New" or "Disabled" to **"Enabled"**
6. Click **OK**
7. **RESTART Audacity** (important!)
8. Keep Audacity open

**Step 2: Run the Processing Script**

```bash
python process_voice_samples.py
```

**What it does:**
- ✅ Connects to Audacity automatically
- ✅ Converts stereo → mono
- ✅ Normalizes audio levels
- ✅ Optional noise reduction
- ✅ Guides you through trimming to 15-25 seconds
- ✅ Exports processed files to `voice_samples_processed/`

---

### Method 2: Manual Processing (If Scripting Doesn't Work)

If the automated script doesn't work, use this step-by-step manual guide:

#### For Each Voice Sample:

**1. Open in Audacity**
   - Drag WAV file into Audacity
   - OR: File → Open → Select your WAV file

**2. Convert Stereo to Mono**
   - Click track dropdown ▼ (small triangle next to track name)
   - Select **"Split Stereo to Mono"**
   - Delete one of the two tracks (click X on the track)
   - OR: **Tracks → Mix → Mix Stereo Down to Mono**

**3. Normalize Audio**
   - Select all: **Ctrl+A** (Windows) or **Cmd+A** (Mac)
   - Go to: **Effect → Volume and Compression → Normalize...**
   - Settings:
     - ✅ Remove DC offset
     - ✅ Normalize peak amplitude to: **-1.0 dB**
     - ❌ Normalize stereo channels independently (uncheck)
   - Click **OK**

**4. Noise Reduction (Optional but Recommended)**
   - Find a 1-2 second section with ONLY background noise (no speech)
   - Select it
   - Go to: **Effect → Noise Removal and Repair → Noise Reduction...**
   - Click **"Get Noise Profile"**
   - Select all audio: **Ctrl+A**
   - Go to: **Effect → Noise Removal and Repair → Noise Reduction...** again
   - Settings:
     - Noise reduction: **12 dB**
     - Sensitivity: **6.00**
     - Frequency smoothing: **3**
   - Click **OK**

**5. Trim to 15-25 Seconds**

This is the most important step! Select the BEST 15-25 seconds:

**What to look for:**
   - ✅ Varied emotions (happy, sad, excited, calm)
   - ✅ Different pitches (high and low)
   - ✅ Different speeds (fast and slow speech)
   - ✅ Both questions and statements
   - ✅ Clear, crisp pronunciation
   - ❌ AVOID: monotone speech, long pauses, background noise

**How to trim:**
   - Click and drag to select your chosen section
   - You'll see the selection duration at the bottom (aim for 15-25 sec)
   - Press **Ctrl+T** (Windows) or **Cmd+T** (Mac)
   - OR: **Edit → Remove Special → Trim Audio**

**6. Remove Silence from Edges**
   - Select the very start (first 0.2 seconds)
   - If it's just silence, press **Delete**
   - Do the same for the end

**7. Export**
   - **File → Export → Export Audio...**
   - Format: **WAV (Microsoft)**
   - Sample Rate: **44100 Hz** (or keep original)
   - Encoding: **Signed 16-bit PCM**
   - Filename: `voice_samples_processed/AiD_Sample_1_processed.wav`
   - Click **Save**

**8. Verify Quality**

After processing, run the quality checker:

```bash
python check_voice_samples.py
```

Point it to your `voice_samples_processed/` directory.

You should see scores of **80-100** instead of the original **25-40**.

---

## Audacity Macros (Batch Processing Alternative)

If the Python script doesn't work, you can create an Audacity Macro:

### Create the Macro:

1. In Audacity: **Tools → Macros...**
2. Click **"New"** and name it: **"Voice Sample Cleanup"**
3. Click **"Insert"** and add these commands in order:

   ```
   StereoToMono
   Normalize: PeakLevel=-1.0 RemoveDcOffset=Yes
   ```

4. Click **"Save"**

### Run on All Files:

1. **Tools → Macros...**
2. Select "Voice Sample Cleanup"
3. Click **"Files..."**
4. Select all your voice sample WAV files
5. Choose output folder
6. Click **OK**

**Then manually:**
- Open each processed file
- Trim to 15-25 seconds of the best speech
- Export

---

## Troubleshooting

### "Could not connect to Audacity"

**Solution:**
1. Make sure Audacity is actually open
2. Check Edit → Preferences → Modules
3. Verify mod-script-pipe is set to "Enabled" (not "New")
4. Restart Audacity completely
5. On first launch after enabling, Audacity may ask to scan effects - let it complete

### "Mod-script-pipe not available"

**Solution:**
1. Update to Audacity 2.4.0 or later
2. Download from: https://www.audacityteam.org/
3. During installation, ensure all modules are selected
4. After install, enable mod-script-pipe in Preferences

### Python script hangs or freezes

**Solution:**
1. Close Audacity completely
2. Restart Audacity
3. Don't open any audio files before running the script
4. Let the script control Audacity
5. If it still hangs, use the manual method instead

### Processed audio sounds worse

**Possible causes:**
1. **Noise reduction too aggressive** - Use 6-12 dB max
2. **Normalization clipping** - Use -1.0 dB, not 0.0 dB
3. **Original sample has issues** - Check original quality
4. **Wrong section selected** - Choose section with clearest speech

**Solutions:**
- Re-process with gentler noise reduction
- Select a different 15-25 second section
- Try a different source audio file

### File is too quiet after processing

**Solution:**
1. Re-open in Audacity
2. Effect → Volume and Compression → Normalize
3. Set to -1.0 dB
4. Make sure "Normalize peak amplitude" is checked

### Still getting low quality scores

**Check these:**
- ✅ Is it mono (1 channel)?
- ✅ Is it 15-25 seconds long?
- ✅ Is it 22050 Hz or 44100 Hz sample rate?
- ✅ Is the volume normalized?
- ✅ Did you remove background noise?
- ✅ Did you select the BEST section (varied speech)?

---

## Tips for Best Results

### Choosing the Best 15-25 Second Section:

**Good examples:**
```
"I'm so excited to tell you about this! You know, sometimes I feel
like we're on the right track, but other times... well, let's just
say it's challenging. What do you think? Should we move forward
with this plan or reconsider?"
```
- Varied emotions ✅
- Questions and statements ✅
- Different speeds ✅
- Natural speech patterns ✅

**Bad examples:**
```
"Hello. This is a test. I am reading this in a monotone voice.
One, two, three, four, five..."
```
- Monotone ❌
- No emotion ❌
- Unnatural ❌

### Multiple Samples:

Process **3-5 of your best samples** rather than all 7. Quality > Quantity!

Choose samples where the speaker:
- Has different emotional states
- Uses different speaking styles
- Covers different pitch ranges
- Has clear, crisp audio

---

## After Processing

### Verify Your Work:

1. **Listen to each processed file**
   - Does it sound natural?
   - Is the volume consistent?
   - No weird artifacts from noise reduction?

2. **Check with the quality analyzer:**
   ```bash
   python check_voice_samples.py
   ```
   Update the script to check `voice_samples_processed/` directory

3. **Test with voice cloning:**
   ```bash
   python test_voice_cloning.py
   ```
   Update to use processed samples

### Expected Results:

**Before processing:**
- Quality scores: 25-40
- Duration: 40-130 seconds
- Stereo audio
- Inconsistent volume

**After processing:**
- Quality scores: 80-100 ✅
- Duration: 15-25 seconds ✅
- Mono audio ✅
- Normalized volume ✅

---

## Quick Reference Card

### Audacity Keyboard Shortcuts:

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Select All | Ctrl+A | Cmd+A |
| Trim | Ctrl+T | Cmd+T |
| Play/Stop | Space | Space |
| Zoom In | Ctrl+1 | Cmd+1 |
| Zoom Out | Ctrl+3 | Cmd+3 |
| Undo | Ctrl+Z | Cmd+Z |

### Optimal Settings:

| Property | Recommended Value |
|----------|------------------|
| Duration | 15-25 seconds |
| Sample Rate | 44100 Hz |
| Channels | 1 (Mono) |
| Bit Depth | 16-bit |
| Normalization | -1.0 dB |
| Noise Reduction | 6-12 dB |

---

## Need Help?

If you're still having issues:
1. Check the error messages carefully
2. Try the manual method instead of automation
3. Process just one file first to test
4. Verify Audacity version is 2.4.0+
5. Make sure you have write permissions to output folder

Good luck! Your processed samples should give you much better voice cloning results! 🎙️
