# Two-Stage Voice Cloning Workflow Guide

## Overview

This guide explains how to use external voice cloning software (Stage 1) to generate high-quality audio samples, then use those outputs as training samples for the AiD voice cloning system (Stage 2).

## Why Two-Stage Approach?

- Work around limited original voice samples
- Pre-process or enhance voice characteristics
- Create variations of a voice
- Improve quality of low-fidelity original recordings

---

## AiD System Requirements (Stage 2)

Your Stage 1 output **MUST** match these specifications:

### ✅ Critical Requirements

| Parameter | Requirement | Notes |
|-----------|-------------|-------|
| **Format** | WAV only | No MP3, FLAC, etc. |
| **Sample Rate** | 22050 Hz or 44100 Hz | Preferred: 22050 Hz |
| **Channels** | Mono (1 channel) | Convert stereo to mono |
| **Duration** | 6-30 seconds | Optimal: 10-20 seconds |
| **Bit Depth** | 16-bit or 32-bit | 16-bit recommended |
| **RMS Level** | ≥ 0.05 (normalized) | Not too quiet |
| **Peak Level** | < 0.95 (normalized) | Avoid clipping |
| **Quality Score** | ≥ 60/100 | Run `check_voice_samples.py` |

### 📁 Sample Storage

Place generated samples in: `/home/user/AiD/voice_samples/`

**Recommended**: 3-7 diverse samples with varied speech patterns

---

## Stage 1: Recommended Tools (2025)

### 🥇 Primary Recommendation: F5-TTS

**Why F5-TTS:**
- Best balance of quality and speed in 2025
- Sub-7 second processing times
- Excellent clarity and articulation
- Emotional depth support
- Multilingual capabilities

**Installation:**
```bash
# Clone repository
git clone https://github.com/SWivid/F5-TTS.git
cd F5-TTS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Usage for Voice Cloning:**
```python
from f5_tts import F5TTS

# Initialize model
model = F5TTS()

# Generate voice from reference samples
# (Use your original voice samples here)
model.clone_voice(
    reference_audio="path/to/original_sample.wav",
    text="Your script text here with varied speech patterns.",
    output_path="output.wav",

    # CRITICAL QUALITY SETTINGS:
    sample_rate=22050,        # Match AiD requirement
    channels=1,                # Mono
    bit_depth=16,              # 16-bit
    normalize=True,            # Normalize audio
    remove_silence=True        # Trim silence
)
```

### 🥈 Alternative: StyleTTS2

**Why StyleTTS2:**
- High-fidelity expressive speech
- Fast training and inference
- Great for audiobook-style narration
- Style diffusion for natural prosody

**Installation:**
```bash
# Clone repository
git clone https://github.com/yl4579/StyleTTS2.git
cd StyleTTS2

# Install dependencies
pip install -r requirements.txt

# Download pretrained models
python download_models.py
```

**Usage:**
```python
import styletts2

# Initialize
tts = styletts2.StyleTTS2()

# Generate with voice cloning
output = tts.synthesize(
    text="Your varied speech script here.",
    reference_audio="path/to/original_sample.wav",

    # QUALITY SETTINGS:
    sample_rate=22050,
    output_format="wav",
    bit_depth=16,
    channels=1
)

output.save("output.wav")
```

### ⚡ Enhancement Tool: RVC (Optional)

**Why RVC:**
- Refines vocal characteristics (melody, timbre)
- Post-processes TTS output for naturalness
- Can enhance F5-TTS or StyleTTS2 output

**When to use:** As a post-processing step after F5-TTS/StyleTTS2 to further enhance quality

**Installation:**
```bash
# Clone RVC repository
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

# Install
pip install -r requirements.txt
```

---

## Stage 1 Workflow: Best Practices

### 1. Prepare Your Original Samples

**Before generating Stage 1 output:**

- ✅ Use highest quality original recordings available
- ✅ Clean audio (remove background noise)
- ✅ Multiple samples (3-5) showing voice variety
- ✅ Each sample 10-30 seconds
- ✅ Varied emotions, pitches, speaking styles

### 2. Generate Stage 1 Samples

**Quality Maximization Settings:**

```python
# Example with F5-TTS
QUALITY_SETTINGS = {
    "sample_rate": 22050,      # AiD optimal
    "channels": 1,              # Mono only
    "bit_depth": 16,            # Standard quality
    "normalize": True,          # Consistent volume
    "remove_silence": True,     # Clean edges
    "noise_reduction": True,    # Remove artifacts
    "peak_limit": 0.90,         # Prevent clipping
    "rms_target": 0.15          # Good volume level
}

# Generate multiple varied samples
scripts = [
    "This is a sample with normal speaking pace and neutral emotion.",
    "Here's an example with slightly varied intonation and rhythm!",
    "Let's include some questions? And declarative statements too.",
    "Expressing excitement and energy in this particular sample!",
    "A calm, measured tone works well for variety as well."
]

for i, script in enumerate(scripts, 1):
    model.clone_voice(
        reference_audio="original_voice.wav",
        text=script,
        output_path=f"stage1_sample_{i}.wav",
        **QUALITY_SETTINGS
    )
```

### 3. Quality Control: Post-Processing

**After Stage 1 generation, process each file:**

```python
import librosa
import soundfile as sf
import numpy as np

def post_process_sample(input_file, output_file):
    """Ensure sample meets AiD requirements"""

    # Load audio
    audio, sr = librosa.load(input_file, sr=22050, mono=True)

    # Normalize to prevent clipping (peak < 0.95)
    audio = audio / np.max(np.abs(audio)) * 0.90

    # Check RMS (should be >= 0.05)
    rms = np.sqrt(np.mean(audio**2))
    if rms < 0.05:
        # Amplify if too quiet
        audio = audio * (0.15 / rms)

    # Trim silence from edges
    audio, _ = librosa.effects.trim(audio, top_db=30)

    # Ensure duration is 6-30 seconds
    duration = len(audio) / sr
    if duration < 6:
        print(f"WARNING: {input_file} is only {duration:.1f}s - may be too short")
    elif duration > 30:
        print(f"WARNING: {input_file} is {duration:.1f}s - trimming to 25s")
        audio = audio[:25*sr]

    # Save as 16-bit WAV, mono, 22050 Hz
    sf.write(output_file, audio, 22050, subtype='PCM_16')

    print(f"✅ Processed: {output_file}")
    print(f"   Duration: {len(audio)/sr:.1f}s | RMS: {rms:.3f}")

# Process all Stage 1 samples
for i in range(1, 6):
    post_process_sample(
        f"stage1_sample_{i}.wav",
        f"/home/user/AiD/voice_samples/AiD Voice Sample {i}.wav"
    )
```

### 4. Validate Samples

**Run AiD's quality checker:**

```bash
cd /home/user/AiD
python check_voice_samples.py
```

**Target scores:**
- ✅ **Excellent**: 80-100 points
- ✓ **Good**: 60-79 points
- ⚠️ **Fair**: 40-59 points (usable but not ideal)
- ❌ **Poor**: < 40 points (fix issues)

---

## Complete Two-Stage Pipeline

### Automated Script

Save as `generate_two_stage_samples.py`:

```python
#!/usr/bin/env python3
"""
Two-Stage Voice Cloning Pipeline
Generates high-quality samples for AiD voice cloning
"""

import os
import sys
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path

# Import your chosen Stage 1 tool
# from f5_tts import F5TTS  # Or StyleTTS2, etc.

class TwoStageVoicePipeline:
    def __init__(self, original_sample_path):
        self.original_sample = original_sample_path
        self.output_dir = Path("/home/user/AiD/voice_samples")
        self.output_dir.mkdir(exist_ok=True)

        # Initialize Stage 1 model
        # self.tts_model = F5TTS()

    def generate_varied_scripts(self, count=5):
        """Generate varied text scripts for diversity"""
        scripts = [
            "The quick brown fox jumps over the lazy dog with enthusiasm.",
            "How are you doing today? I hope everything is going well!",
            "This sample demonstrates a calm and measured speaking tone.",
            "Let's include some excitement and energy in our voice!",
            "Reading naturally with varied pitch and rhythm patterns."
        ]
        return scripts[:count]

    def stage1_generate(self, text, output_path):
        """Stage 1: Generate using external TTS"""
        print(f"🎤 Stage 1: Generating with TTS...")

        # Example with F5-TTS (adapt to your chosen tool)
        """
        self.tts_model.clone_voice(
            reference_audio=self.original_sample,
            text=text,
            output_path=output_path,
            sample_rate=22050,
            channels=1,
            bit_depth=16,
            normalize=True,
            remove_silence=True
        )
        """

        # PLACEHOLDER: Replace with actual Stage 1 tool
        print(f"   Generated: {output_path}")

    def stage2_post_process(self, input_file, output_file):
        """Stage 2: Post-process to match AiD requirements"""
        print(f"⚙️  Stage 2: Post-processing...")

        # Load as mono, 22050 Hz
        audio, sr = librosa.load(input_file, sr=22050, mono=True)

        # Normalize peak to 0.90 (prevent clipping at 0.95)
        audio = audio / np.max(np.abs(audio)) * 0.90

        # Check and fix RMS
        rms = np.sqrt(np.mean(audio**2))
        if rms < 0.05:
            audio = audio * (0.15 / rms)
            print(f"   📊 Amplified quiet audio: RMS {rms:.3f} -> 0.15")

        # Trim silence
        audio, _ = librosa.effects.trim(audio, top_db=30)

        # Check duration
        duration = len(audio) / sr
        if duration < 6:
            print(f"   ⚠️  WARNING: Duration {duration:.1f}s is below 6s minimum")
        elif duration > 30:
            audio = audio[:25*sr]
            print(f"   ✂️  Trimmed from {duration:.1f}s to 25s")

        # Save as 16-bit WAV
        sf.write(output_file, audio, 22050, subtype='PCM_16')

        print(f"   ✅ Saved: {output_file}")
        print(f"   📏 Duration: {len(audio)/sr:.1f}s | RMS: {rms:.3f}\n")

    def run_pipeline(self, num_samples=5):
        """Execute complete two-stage pipeline"""
        print("=" * 60)
        print("TWO-STAGE VOICE CLONING PIPELINE")
        print("=" * 60)
        print(f"Original sample: {self.original_sample}")
        print(f"Output directory: {self.output_dir}")
        print(f"Generating {num_samples} samples...\n")

        scripts = self.generate_varied_scripts(num_samples)

        for i, script in enumerate(scripts, 1):
            print(f"[{i}/{num_samples}] Processing sample {i}...")
            print(f"📝 Text: \"{script[:50]}...\"")

            # Stage 1: Generate with external TTS
            temp_file = f"/tmp/stage1_temp_{i}.wav"
            self.stage1_generate(script, temp_file)

            # Stage 2: Post-process for AiD
            final_file = self.output_dir / f"AiD Voice Sample {i}.wav"
            self.stage2_post_process(temp_file, final_file)

            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)

        print("=" * 60)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 60)
        print(f"\nGenerated {num_samples} samples in: {self.output_dir}")
        print("\nNext steps:")
        print("1. Run quality check: python check_voice_samples.py")
        print("2. Test voice cloning: python test_voice_cloning.py")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_two_stage_samples.py <original_voice_sample.wav>")
        sys.exit(1)

    original_sample = sys.argv[1]

    if not os.path.exists(original_sample):
        print(f"❌ Error: File not found: {original_sample}")
        sys.exit(1)

    pipeline = TwoStageVoicePipeline(original_sample)
    pipeline.run_pipeline(num_samples=5)
```

---

## Quality Checklist

### Before Stage 1 Generation:
- [ ] Original samples are highest quality available
- [ ] Background noise removed from originals
- [ ] Multiple original samples (3-5) prepared
- [ ] Scripts prepared with varied speech patterns

### During Stage 1 Generation:
- [ ] Sample rate set to 22050 Hz
- [ ] Mono output (1 channel)
- [ ] 16-bit depth
- [ ] Normalization enabled
- [ ] Silence removal enabled

### After Stage 1 (Post-Processing):
- [ ] Converted to WAV format
- [ ] Trimmed silence from edges
- [ ] Normalized to prevent clipping (peak < 0.95)
- [ ] RMS level checked (≥ 0.05)
- [ ] Duration verified (6-30 seconds)
- [ ] Ran `check_voice_samples.py`
- [ ] Quality score ≥ 60 points

### Stage 2 (AiD Usage):
- [ ] All samples in `/home/user/AiD/voice_samples/`
- [ ] Ran `test_voice_cloning.py` successfully
- [ ] Output quality acceptable

---

## Troubleshooting

### ❌ Quality Score Below 60

**Check:**
1. Run `python check_voice_samples.py` for specific issues
2. Look for: sample rate, duration, RMS, clipping warnings
3. Reprocess samples using post-processing script

### ❌ "Audio may be clipping"

**Solution:**
```python
# Reduce peak normalization
audio = audio / np.max(np.abs(audio)) * 0.85  # Lower from 0.90
```

### ❌ "Too quiet (RMS < 0.05)"

**Solution:**
```python
# Amplify audio
target_rms = 0.15
audio = audio * (target_rms / current_rms)
```

### ❌ "Duration too short"

**Solution:**
- Generate longer scripts in Stage 1 (aim for 15-20 seconds)
- Combine multiple short samples

### ❌ Stereo Audio Detected

**Solution:**
```python
# Force mono conversion
audio, sr = librosa.load(file, sr=22050, mono=True)
```

---

## Expected Results

### Quality Comparison

| Approach | Expected Quality | Artifacts | Time |
|----------|------------------|-----------|------|
| **Original samples only** | ⭐⭐⭐⭐⭐ | Minimal | Fast |
| **Two-stage (F5-TTS)** | ⭐⭐⭐⭐ | Low | Medium |
| **Two-stage (StyleTTS2)** | ⭐⭐⭐⭐ | Low | Medium |
| **Two-stage + RVC enhancement** | ⭐⭐⭐⭐ | Medium | Slow |

### When Two-Stage Works Best

✅ **Good use cases:**
- Original samples are low quality/noisy
- Limited original samples (1-2 clips)
- Need to create sample variations
- Original samples too short

❌ **Poor use cases:**
- High-quality original samples available (3+)
- Original samples already meet AiD requirements
- Need maximum fidelity (use originals directly)

---

## Next Steps

1. **Choose Stage 1 tool**: F5-TTS (recommended) or StyleTTS2
2. **Install dependencies**: Follow installation section
3. **Prepare original samples**: Clean, high-quality source audio
4. **Run pipeline**: Use automated script or manual workflow
5. **Validate quality**: `python check_voice_samples.py`
6. **Test cloning**: `python test_voice_cloning.py`

---

## Resources

- **F5-TTS**: https://github.com/SWivid/F5-TTS
- **StyleTTS2**: https://github.com/yl4579/StyleTTS2
- **RVC**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- **AiD Voice Cloning Setup**: `VOICE_CLONING_SETUP.md`
- **Quality Checker**: `check_voice_samples.py`

---

## Support

For issues:
1. Check `check_voice_samples.py` output for specific problems
2. Review quality scores and recommendations
3. Adjust Stage 1 settings or post-processing parameters
4. Regenerate samples if quality score < 60

**Quality target**: 80+ points for excellent results, 60+ minimum for acceptable cloning.
