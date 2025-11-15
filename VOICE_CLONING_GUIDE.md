# AiD Voice Cloning Setup Guide

This guide explains how to set up voice cloning for AiD using the hybrid approach: **GPT-SoVITS for sample generation + Coqui TTS for runtime synthesis**.

## Why This Approach?

✅ **No bloat** - GPT-SoVITS stays external, AiD only needs lightweight Coqui TTS (~100MB)
✅ **High quality** - GPT-SoVITS generates professional-grade samples
✅ **Fast runtime** - Coqui TTS generates speech in 1-3 seconds
✅ **Flexible** - Swap samples anytime without changing code
✅ **Dynamic** - Can speak ANY text, not just pre-generated phrases

---

## Step 1: Generate Voice Samples with GPT-SoVITS

### Install GPT-SoVITS

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RVC-Boss/GPT-SoVITS.git
   cd GPT-SoVITS
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download pre-trained models:**
   ```bash
   python download_models.py
   ```

### Prepare Your Voice Samples

For best results, record 5-10 audio samples with the following characteristics:

**Recording Guidelines:**
- **Duration**: 10-30 seconds each
- **Format**: WAV (44.1kHz or 48kHz, 16-bit)
- **Environment**: Quiet room, no background noise
- **Content**: Natural speech with varied emotions/tones
- **Quality**: Clear, consistent volume

**Recommended Sample Types:**
- `neutral_01.wav` - Calm, informative tone
- `happy_01.wav` - Cheerful, upbeat tone
- `thoughtful_01.wav` - Contemplative, serious tone
- `energetic_01.wav` - Excited, enthusiastic tone
- `empathetic_01.wav` - Caring, understanding tone

### Generate High-Quality Voice with GPT-SoVITS

1. **Run the web interface:**
   ```bash
   python webui.py
   ```

2. **Upload your recordings** in the interface

3. **Train/Fine-tune** (optional but recommended for best quality)

4. **Generate samples:**
   - Input various test phrases with different emotional tones
   - Generate 5-10 samples (10-30 seconds each)
   - Download the generated audio files

5. **Save samples** to AiD's directory:
   ```bash
   # Copy generated samples to AiD
   cp generated_samples/*.wav /path/to/AiD/voice_samples/reference/
   ```

---

## Step 2: Install AiD Voice Dependencies

Install the required packages for AiD's voice cloning:

```bash
cd /path/to/AiD
pip install TTS sounddevice soundfile pyttsx3 SpeechRecognition pyaudio
```

**What each package does:**
- `TTS` - Coqui TTS for voice cloning (100MB)
- `sounddevice` - Audio playback
- `soundfile` - Audio file handling
- `pyttsx3` - Fallback TTS engine
- `SpeechRecognition` - Speech-to-text
- `pyaudio` - Microphone input

---

## Step 3: Configure AiD

### Verify Your Setup

1. **Check samples are in place:**
   ```bash
   ls voice_samples/reference/
   # Should show: neutral_01.wav, happy_01.wav, etc.
   ```

2. **Configure settings** (optional):
   Edit `voice_config.json` to customize:
   - TTS engine preference
   - Audio quality settings
   - CUDA acceleration (if you have NVIDIA GPU)

### Test Voice Cloning

Run the test script to verify everything works:

```bash
python test_voice_cloning.py
```

This will:
1. Load your reference samples
2. Generate test speech with cloned voice
3. Play the audio
4. Save output to `test_voice_output.wav`

---

## Step 4: Usage

### Basic Usage

```python
from voice_handler import speak

# Speak with cloned voice
speak("Hello! I am AID with my custom cloned voice.")
```

### Check Voice Status

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

### Save Generated Audio

```python
from voice_handler import get_voice

voice = get_voice()
voice.speak("This will be saved to a file.", output_file="output.wav")
```

---

## Troubleshooting

### "No reference audio found"

**Problem:** AiD can't find your voice samples.

**Solution:**
1. Check samples are in `voice_samples/reference/`
2. Verify file format (WAV, MP3, FLAC, or OGG)
3. Check file permissions

### "Coqui TTS initialization error"

**Problem:** Coqui TTS failed to load.

**Solution:**
1. Install/reinstall TTS: `pip install TTS`
2. Check internet connection (first run downloads models)
3. AiD will automatically fall back to pyttsx3

### "sounddevice/soundfile not installed"

**Problem:** Audio playback libraries missing.

**Solution:**
```bash
pip install sounddevice soundfile
```

### Poor Voice Quality

**Problem:** Generated voice doesn't sound like your samples.

**Solution:**
1. Use higher quality reference samples (44.1kHz+)
2. Add more samples (5-10 recommended)
3. Ensure samples are varied in tone/emotion
4. Re-generate samples with GPT-SoVITS fine-tuning

### Slow Generation

**Problem:** Takes 10+ seconds to generate speech.

**Solution:**
1. Enable CUDA in `voice_config.json` (if you have NVIDIA GPU)
2. Reduce sample count to 3-5
3. Use shorter reference audio (10-15 seconds)

---

## Advanced: Updating Voice Samples

To change AiD's voice:

1. **Generate new samples** with GPT-SoVITS
2. **Replace samples** in `voice_samples/reference/`
3. **Restart AiD** - new voice will be loaded automatically

No code changes needed!

---

## Technical Details

### How It Works

1. **Initialization:**
   - AiD loads reference samples from `voice_samples/reference/`
   - Coqui TTS model (XTTS v2) is initialized
   - First sample is used as primary voice reference

2. **Speech Generation:**
   - Text is cleaned (remove markdown, emojis, URLs)
   - Coqui TTS synthesizes speech using reference audio
   - Audio is played via sounddevice
   - Optional: Save to file

3. **Fallback:**
   - If Coqui fails, AiD falls back to pyttsx3
   - Robotic voice, but always works

### Model Information

**XTTS v2 (Default):**
- Multi-speaker, multilingual TTS
- Supports voice cloning from 10-30 second samples
- 22.05kHz output
- ~100MB model size
- 1-3 second generation time (CPU)

### File Structure

```
AiD/
├── voice_handler.py          # Voice cloning implementation
├── voice_config.json          # Configuration settings
├── VOICE_CLONING_GUIDE.md    # This file
├── test_voice_cloning.py     # Test script
└── voice_samples/
    ├── reference/             # Your GPT-SoVITS samples (place here)
    │   ├── neutral_01.wav
    │   ├── happy_01.wav
    │   └── ...
    └── generated/             # Auto-generated outputs (optional)
```

---

## FAQ

### Q: Do I need to use GPT-SoVITS again after setup?

**A:** No! Once you generate samples and place them in `voice_samples/reference/`, you're done. Only regenerate if you want to change the voice.

### Q: Can I use pre-recorded audio instead of GPT-SoVITS?

**A:** Yes! Any high-quality audio samples work. GPT-SoVITS just ensures professional quality.

### Q: How many samples do I need?

**A:** Minimum 1, recommended 5-10 for best variety and quality.

### Q: Can AiD speak multiple languages?

**A:** Yes! XTTS v2 supports 17 languages. Change `language` in `voice_config.json`.

### Q: Will this work offline?

**A:** Yes! After initial model download, everything runs locally offline.

### Q: What if I don't have a GPU?

**A:** No problem! Coqui TTS works on CPU (1-3 seconds per phrase). GPU just makes it faster (<1 second).

---

## Next Steps

1. ✅ Generate voice samples with GPT-SoVITS
2. ✅ Install dependencies: `pip install TTS sounddevice soundfile`
3. ✅ Place samples in `voice_samples/reference/`
4. ✅ Run test: `python test_voice_cloning.py`
5. ✅ Enjoy your custom AiD voice!

---

**Need Help?** Check the [Coqui TTS documentation](https://docs.coqui.ai/) or [GPT-SoVITS repository](https://github.com/RVC-Boss/GPT-SoVITS).
