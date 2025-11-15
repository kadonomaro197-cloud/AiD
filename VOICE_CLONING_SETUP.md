# Voice Cloning Setup Guide

This guide will help you set up voice cloning for AiD using Coqui TTS with XTTSv2.

## Prerequisites

### 1. Install Dependencies

```bash
# Install Coqui TTS
pip install TTS

# Install PyTorch (choose based on your system)
# For CPU only:
pip install torch

# For NVIDIA GPU (CUDA):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Prepare Voice Samples

Create a `voice_samples` directory in your AiD project root:

```bash
mkdir voice_samples
```

Add WAV files of the voice you want to clone:
- **Format**: WAV, 22050 Hz or 44100 Hz sample rate
- **Duration**: 6-30 seconds per sample (optimal)
- **Quality**: Clear audio, minimal background noise
- **Multiple samples**: Better results with 3-7 diverse samples

**Naming convention**:
- `AiD Voice Sample 1.wav`
- `AiD Voice Sample 2.wav`
- etc.

### 3. Voice Sample Tips

For best results:
- Use samples with varied intonation and emotion
- Ensure consistent audio quality across samples
- Avoid clipping or distortion
- Remove silence from start/end
- Use samples from the same speaker/character

## Running the Test

```bash
python test_voice_cloning.py
```

### What the test does:

1. ✅ Checks for voice samples in `voice_samples/` directory
2. ✅ Verifies dependencies (Coqui TTS, PyTorch)
3. ✅ Downloads XTTSv2 model (~2GB, first run only)
4. ✅ Initializes voice handler
5. ✅ Generates test audio with cloned voice
6. ✅ Creates `test_cloned_output.wav`

### First Run Note

The first time you run the test, it will:
- Download the XTTSv2 model (~2GB)
- This may take 5-15 minutes depending on your internet speed
- The model is cached for future use

## Expected Output

```
Starting voice cloning test...

============================================================
AiD Voice Cloning Test
============================================================

✓ Found 7 voice sample(s):
  1. AiD Voice Sample 1.wav (13.39 MB)
  ...

[1/5] Importing voice handler...
✓ Voice handler imported successfully

[2/5] Checking dependencies...
✓ Coqui TTS available
✓ PyTorch available (Device: CPU)

[3/5] Initializing TTS engine...
✓ XTTSv2 model loaded successfully

[4/5] Testing voice cloning...
✓ Generated cloned voice: test_cloned_output.wav (245.32 KB)

[5/5] Test Summary
✅ All tests passed successfully!
```

## Troubleshooting

### Error: "init_voice() missing 1 required positional argument: 'bot'"

**Solution**: Update your voice_handler.py to the latest version. The function signature has been updated to:

```python
def init_voice(bot=None):
    """Initialize voice handler with optional bot parameter."""
```

### Error: "No module named 'TTS'"

**Solution**: Install Coqui TTS:
```bash
pip install TTS
```

### Error: "No WAV files found in voice_samples"

**Solution**:
1. Create the `voice_samples` directory
2. Add WAV files of the voice you want to clone
3. Ensure files have `.wav` extension

### CUDA/GPU Issues

If you have an NVIDIA GPU but it's not being detected:

```bash
# Check PyTorch CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Reinstall PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Model Download Fails

If the XTTSv2 model download fails:
1. Check your internet connection
2. Try again (the download will resume)
3. Manually download from Coqui TTS model hub

## Integration with Discord Bot

Once voice cloning works, integrate it with your Discord bot:

```python
# In bot.py
import voice_handler

# Initialize voice handler with bot instance
voice_handler.init_voice(bot)

# Generate voice response
async def speak_in_voice_channel(text, voice_channel):
    # Generate cloned voice audio
    from TTS.api import TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    output_file = "response.wav"
    tts.tts_to_file(
        text=text,
        file_path=output_file,
        speaker_wav="voice_samples/AiD Voice Sample 1.wav",
        language="en"
    )

    # Play in Discord voice channel
    voice_client = await voice_channel.connect()
    voice_client.play(discord.FFmpegPCMAudio(output_file))
```

## Performance Notes

- **CPU**: Works but slower (5-15 seconds per generation)
- **GPU**: Much faster (1-3 seconds per generation)
- **Model size**: ~2GB disk space
- **RAM usage**: ~4GB during inference

## Next Steps

1. ✅ Run `python test_voice_cloning.py`
2. ✅ Listen to `test_cloned_output.wav` to verify quality
3. ✅ Try different voice samples to find best results
4. ✅ Integrate with Discord bot for voice channel support
5. ✅ Consider caching generated audio for common phrases

## Resources

- [Coqui TTS Documentation](https://github.com/coqui-ai/TTS)
- [XTTSv2 Model Card](https://huggingface.co/coqui/XTTS-v2)
- [Voice Cloning Best Practices](https://github.com/coqui-ai/TTS/wiki/XTTS-v2)
