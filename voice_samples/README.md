# Voice Samples Directory

This directory contains voice samples for AiD's TTS voice cloning.

## Requirements

For optimal voice cloning with Coqui XTTSv2, you need:
- **Minimum**: 6-10 seconds of clean audio
- **Recommended**: 2-10 minutes of audio (you have 8+ minutes - perfect!)
- **Format**: WAV files (16-bit, 22050 Hz or 24000 Hz sample rate)
- **Quality**: Clear speech, minimal background noise
- **Content**: Natural, conversational speech with varied intonation

## File Placement

Place your 7 WAV files in this directory:
```
voice_samples/
├── sample_01.wav
├── sample_02.wav
├── sample_03.wav
├── sample_04.wav
├── sample_05.wav
├── sample_06.wav
└── sample_07.wav
```

You can name them anything you like - the system will automatically detect all `.wav` files in this directory.

## Audio Preparation Tips

If you need to prepare your audio samples:

1. **Convert to WAV** (if needed):
   ```bash
   ffmpeg -i input.mp3 -ar 22050 -ac 1 -sample_fmt s16 output.wav
   ```

2. **Remove background noise** (optional):
   - Use Audacity with noise reduction
   - Use FFmpeg with audio filters

3. **Split long recordings** (if needed):
   - Each file should be 10 seconds to 3 minutes
   - Natural speech segments work best

## Voice Quality Checks

Good voice samples should have:
- ✅ Clear pronunciation
- ✅ Natural emotion and intonation
- ✅ Minimal background noise
- ✅ Consistent volume levels
- ✅ Varied speech patterns (questions, statements, emotions)

Avoid:
- ❌ Music or sound effects overlapping speech
- ❌ Multiple speakers talking
- ❌ Heavy compression artifacts
- ❌ Extremely quiet or loud sections

## Testing Your Voice

After placing your samples here, run:
```bash
python test_voice_cloning.py
```

This will test the voice cloning and generate a sample output.
