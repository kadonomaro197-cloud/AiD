# Voice Cloning Quick Start

Get AiD speaking with a custom cloned voice in 3 steps!

## TL;DR

1. **Generate voice samples** with GPT-SoVITS (external tool)
2. **Copy samples** to `voice_samples/reference/`
3. **Install dependencies** and test: `pip install -r requirements.txt && python test_voice_cloning.py`

---

## The Hybrid Approach

**External (GPT-SoVITS):** Generate high-quality voice samples once
↓
**Save samples:** Store in `voice_samples/reference/`
↓
**AiD (Coqui TTS):** Use samples for dynamic voice cloning

**Result:**
- ✅ No bloat (~100MB vs 1-4GB)
- ✅ High quality (90% of GPT-SoVITS)
- ✅ Fast (1-3 seconds)
- ✅ Can speak ANY text

---

## Step 1: Generate Samples (One-Time)

Use **GPT-SoVITS** to create 5-10 voice samples:

```bash
# Install GPT-SoVITS (external, not part of AiD)
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
pip install -r requirements.txt
python download_models.py

# Run the interface
python webui.py
```

**In the GPT-SoVITS interface:**
1. Upload your voice recordings (or record directly)
2. Train/fine-tune the model
3. Generate 5-10 samples with different tones:
   - Neutral
   - Happy
   - Thoughtful
   - Energetic
   - Empathetic
4. Download generated WAV files

See [`VOICE_CLONING_GUIDE.md`](VOICE_CLONING_GUIDE.md) for detailed instructions.

---

## Step 2: Add Samples to AiD

Copy your generated samples to AiD:

```bash
cd /path/to/AiD
cp /path/to/gpt-sovits/outputs/*.wav voice_samples/reference/
```

**Verify samples:**
```bash
ls voice_samples/reference/
# Should show: neutral_01.wav, happy_01.wav, etc.
```

---

## Step 3: Install & Test

**Install dependencies:**
```bash
pip install -r requirements.txt
```

This installs:
- `TTS` - Coqui TTS (~100MB)
- `sounddevice` - Audio playback
- `soundfile` - Audio handling
- `pyttsx3` - Fallback TTS

**Test setup:**
```bash
python test_voice_cloning.py
```

Expected output:
```
============================================================
AiD Voice Cloning Test
============================================================

[1/5] Checking for reference samples...
✅ Found 5 reference sample(s):
   - neutral_01.wav
   - happy_01.wav
   - ...

[2/5] Testing voice_handler import...
✅ voice_handler imported successfully

[3/5] Initializing voice handler...
[VOICE] TTS initialized with Coqui TTS (voice cloning)
[VOICE] Using 5 reference sample(s)
✅ Voice handler initialized

[4/5] Checking voice features...
TTS Enabled: True
TTS Mode: coqui
Voice Cloning: True
Reference Samples: 5
STT Enabled: True

✅ Voice cloning is active!

[5/5] Testing speech generation...
Generating: "Hello! I am AID with my custom cloned voice. This is a test."
✅ Speech generated successfully!
   Saved to: test_voice_output.wav

============================================================
Test Summary
============================================================
✅ Voice cloning test PASSED
   Mode: coqui
   Reference samples: 5

🎉 Your custom voice is ready to use!
   Try speaking with AiD using the voice_handler module.
```

---

## Usage

### Basic Example

```python
from voice_handler import speak

# Speak with cloned voice
speak("Hello! I am AID with my custom voice.")
```

### Save Audio File

```python
from voice_handler import get_voice

voice = get_voice()
voice.speak("This will be saved.", output_file="output.wav")
```

### Check Status

```python
from voice_handler import is_voice_available

status = is_voice_available()
print(status)
# {
#   'tts': True,
#   'tts_mode': 'coqui',
#   'voice_cloning': True,
#   'reference_samples': 5,
#   'stt': True
# }
```

---

## Fallback Mode

If Coqui TTS is not available, AiD automatically falls back to **pyttsx3**:

- ✅ Always works (no dependencies needed)
- ⚠️ Robotic voice (no cloning)
- ✅ Instant (no generation time)

To switch back to voice cloning, install TTS and add samples.

---

## Troubleshooting

### No samples found
```bash
ls voice_samples/reference/
# Should NOT be empty
```

**Fix:** Copy your GPT-SoVITS samples there

### "Coqui TTS initialization error"
```bash
pip install TTS sounddevice soundfile
```

### Poor quality
- Use higher quality samples (44.1kHz+)
- Add more samples (5-10 recommended)
- Re-generate with GPT-SoVITS fine-tuning

---

## Next Steps

- 📖 Read full guide: [`VOICE_CLONING_GUIDE.md`](VOICE_CLONING_GUIDE.md)
- ⚙️ Customize settings: Edit `voice_config.json`
- 🔧 Update voice: Replace samples in `voice_samples/reference/`

**Only need to use GPT-SoVITS once!** After generating samples, AiD handles everything else.
