# Voice Reference Samples

This directory should contain audio samples of the voice you want AID to clone for Text-to-Speech (TTS).

## Setup Instructions

1. **Prepare voice samples**: You need at least one audio file in a supported format (`.wav`, `.mp3`, `.flac`, or `.ogg`)

2. **Quality requirements**:
   - Clean audio with minimal background noise
   - Clear speech without music
   - 5-10 seconds of audio is ideal
   - Mono or stereo audio both work

3. **Place files here**: Copy your voice samples to this directory
   Example: `voice_samples/reference/my_voice.wav`

4. **Configure TTS**: Edit `voice_config.py` to adjust voice parameters:
   - `REFERENCE_SAMPLE_INDEX`: Which sample to use (0 for first, -1 for random)
   - `TEMPERATURE`, `SPEED`, etc.: Fine-tune voice characteristics

5. **Test**: Restart AID and it should automatically use Coqui TTS with voice cloning!

## Fallback Behavior

- If no reference audio is found here, AID will fall back to `pyttsx3` (system TTS)
- The fallback TTS won't have voice cloning capabilities but will still work

## Supported Formats

- `.wav` - Recommended for best quality
- `.mp3` - Common audio format
- `.flac` - Lossless compression
- `.ogg` - Open-source format
