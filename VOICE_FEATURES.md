# 🎙️ AiD Voice Features Documentation

## Overview

AiD now supports voice communication through Discord voice channels! She can speak with a British female voice using Coqui TTS and understand your speech using OpenAI Whisper.

## Features

### ✨ Main Capabilities
- **Voice Channel Integration**: AiD joins Discord voice channels on command
- **Text-to-Speech (TTS)**: British female voice using Coqui TTS (VCTK p225)
- **Speech-to-Text (STT)**: Speech recognition using OpenAI Whisper
- **Dual Output**: All responses appear in both voice AND text chat (for reference)
- **Seamless Switching**: Easy commands to switch between voice and text modes

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg (Required for Discord Voice)

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### 3. Download TTS Models (Automatic on First Run)

On first use, Coqui TTS will automatically download the required models (~150MB). This may take a few minutes.

### 4. Download Whisper Models (Automatic on First Run)

On first use, Whisper will download the base model (~150MB). You can configure different model sizes:

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny  | 39 MB | Fastest | Lower |
| base  | 74 MB | Fast | Good ✅ (default) |
| small | 244 MB | Medium | Better |
| medium | 769 MB | Slow | Very Good |
| large | 1550 MB | Slowest | Best |

To change the model, edit `voice_handler.py` line 34:
```python
STT_MODEL = "base"  # Change to: "tiny", "small", "medium", or "large"
```

## Usage

### Voice Commands

#### Switch to Voice Mode
1. Join a Discord voice channel
2. Type in any text channel:
   ```
   switch to voice
   ```
3. AiD will join your voice channel and confirm in both voice and text

#### Exit Voice Mode
While in voice or text chat, type or say:
```
back to the chat
```
AiD will say goodbye in voice, leave the channel, and return to text-only mode.

### How It Works

#### When in Voice Mode:
- **Your Messages**: Type in text chat as normal (STT from Discord voice coming in future update)
- **AiD's Responses**: She speaks in voice AND sends text to chat
- **Text Reference**: Every response appears in text chat so you can read and refer back

#### Example Conversation:

```
You (text): Hey AiD, switch to voice
AiD (voice + text): Alright boss, I'm in the voice channel now! You can talk to me or text me, innit?

You (text): What's the weather like?
AiD (voice + text): Dunno mate, I don't have weather data. But I can help ya with other stuff!

You (text): back to the chat
AiD (voice + text): Alright boss, heading back to text chat. Catch ya there!
```

## Configuration

### Voice Settings

Edit `voice_handler.py` to customize:

```python
# Line 33-37: TTS/STT Models
TTS_MODEL = "tts_models/en/vctk/vits"  # TTS model
STT_MODEL = "base"                      # Whisper model size
VOICE_CHARACTER = "p225"                # British female voice

# Available voices (VCTK dataset):
# p225 - Female British (default)
# p226 - Male British
# p227 - Male British
# p228 - Female British
# ... and many more
```

### Performance Tips

1. **GPU Acceleration**: If you have a CUDA-capable GPU, install GPU versions:
   ```bash
   pip uninstall torch
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Faster TTS**: For quicker response times, use a lighter TTS model:
   ```python
   TTS_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"  # Faster, single voice
   ```

3. **Memory Usage**: The base Whisper model uses ~500MB RAM. Use "tiny" for lower memory systems.

## Troubleshooting

### "Voice handler ain't ready yet"
- Check console logs for initialization errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify FFmpeg is installed: `ffmpeg -version`

### "Oi, mate! Ya need to be in a voice channel first"
- Join a Discord voice channel before typing "switch to voice"

### No Audio in Voice Channel
- Check bot permissions: Needs "Connect" and "Speak" in voice channels
- Verify FFmpeg is in system PATH
- Check Discord voice channel region compatibility

### TTS/STT Not Initializing
- Check console for specific error messages
- Verify PyTorch is installed: `python -c "import torch; print(torch.__version__)"`
- Try reinstalling TTS: `pip uninstall TTS && pip install TTS`

### Audio Quality Issues
- Increase Whisper model size for better transcription
- Check microphone quality and Discord voice settings
- Ensure stable internet connection (models download on first use)

## Technical Details

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Discord Message                       │
│                  "switch to voice"                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   auto_response.py     │
        │  (Command Detection)   │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │   voice_handler.py     │
        │  (DiscordVoiceManager) │
        └────┬──────────────┬────┘
             │              │
             ▼              ▼
    ┌────────────┐  ┌──────────────┐
    │  TTS (p225)│  │ Discord Voice│
    │   Coqui    │  │   Channel    │
    └────────────┘  └──────────────┘
```

### Response Flow (Voice Mode Active)

```
User Message → call_aid_api() → Generate Response
                                       │
                        ┌──────────────┴─────────────┐
                        │                            │
                        ▼                            ▼
              ┌─────────────────┐         ┌──────────────────┐
              │  TTS Generation │         │ Discord Text Chat│
              │  (Coqui TTS)    │         │  (Reference)     │
              └────────┬────────┘         └──────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Discord Voice   │
              │ (FFmpeg PCM)    │
              └─────────────────┘
```

### File Structure

```
AiD/
├── bot.py                  # Main bot, initializes voice handler
├── auto_response.py        # Voice command detection & dual output
├── voice_handler.py        # Voice system implementation
├── requirements.txt        # Dependencies including TTS/STT
└── VOICE_FEATURES.md      # This documentation
```

## Future Enhancements

- [ ] Voice input via Discord voice (STT from mic)
- [ ] Voice activity detection for automatic listening
- [ ] Multiple voice options (accents, personalities)
- [ ] Emotion-aware voice modulation
- [ ] Voice command shortcuts
- [ ] Audio effects and filters

## Contributing

Found a bug or have a suggestion? Please:
1. Check existing issues
2. Create a detailed bug report
3. Include console logs and system info

## License

Part of the AiD project. See main project license.

---

**Created by**: Dee
**Version**: 1.0
**Last Updated**: 2025-11-15
