# Voice Samples Directory

This directory stores reference audio samples for AiD's voice cloning.

## Directory Structure

```
voice_samples/
├── reference/          # High-quality GPT-SoVITS generated samples (place your samples here)
└── README.md          # This file
```

## How to Add Voice Samples

1. **Generate samples with GPT-SoVITS** (see VOICE_CLONING_GUIDE.md in the root directory)
2. **Save samples** as WAV or MP3 files in `reference/`
3. **Recommended**: 5-10 samples, 10-30 seconds each, covering different emotions/tones

## Sample Naming Convention

Use descriptive names for your samples:
- `neutral_01.wav` - Calm, neutral tone
- `happy_01.wav` - Cheerful, upbeat tone
- `thoughtful_01.wav` - Contemplative, serious tone
- `energetic_01.wav` - Excited, enthusiastic tone

AiD will automatically detect and use samples from this directory.
