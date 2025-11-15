#!/usr/bin/env python3
"""
Voice Cloning Test Script for AiD

This script tests the voice cloning functionality with Coqui TTS.
Run this after setting up voice samples in voice_samples/reference/

Usage:
    python test_voice_cloning.py
"""

import sys
from pathlib import Path

def test_voice_cloning():
    """Test voice cloning setup and functionality."""

    print("=" * 60)
    print("AiD Voice Cloning Test")
    print("=" * 60)
    print()

    # Check for reference samples
    print("[1/5] Checking for reference samples...")
    samples_dir = Path("voice_samples/reference")

    if not samples_dir.exists():
        print("❌ voice_samples/reference/ directory not found!")
        print("   Run: mkdir -p voice_samples/reference")
        return False

    audio_files = list(samples_dir.glob("*.wav")) + \
                  list(samples_dir.glob("*.mp3")) + \
                  list(samples_dir.glob("*.flac")) + \
                  list(samples_dir.glob("*.ogg"))

    if not audio_files:
        print("❌ No audio samples found in voice_samples/reference/")
        print("   Please add voice samples generated with GPT-SoVITS")
        print("   See VOICE_CLONING_GUIDE.md for instructions")
        return False

    print(f"✅ Found {len(audio_files)} reference sample(s):")
    for audio_file in audio_files:
        print(f"   - {audio_file.name}")
    print()

    # Test voice handler import
    print("[2/5] Testing voice_handler import...")
    try:
        from voice_handler import get_voice, is_voice_available
        print("✅ voice_handler imported successfully")
        print()
    except ImportError as e:
        print(f"❌ Failed to import voice_handler: {e}")
        return False

    # Initialize voice handler
    print("[3/5] Initializing voice handler...")
    try:
        voice = get_voice()
        print("✅ Voice handler initialized")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize voice handler: {e}")
        return False

    # Check voice availability
    print("[4/5] Checking voice features...")
    status = is_voice_available()

    print(f"TTS Enabled: {status['tts']}")
    print(f"TTS Mode: {status['tts_mode']}")
    print(f"Voice Cloning: {status['voice_cloning']}")
    print(f"Reference Samples: {status['reference_samples']}")
    print(f"STT Enabled: {status['stt']}")
    print()

    if not status['tts']:
        print("❌ TTS is not enabled")
        print("   Install dependencies: pip install TTS sounddevice soundfile")
        return False

    if status['tts_mode'] != 'coqui':
        print("⚠️  Using fallback TTS (pyttsx3) instead of voice cloning")
        print("   Install Coqui TTS: pip install TTS sounddevice soundfile")
        print("   Add reference samples to voice_samples/reference/")
    else:
        print("✅ Voice cloning is active!")
    print()

    # Test speech generation
    print("[5/5] Testing speech generation...")
    test_text = "Hello! I am AID with my custom cloned voice. This is a test."

    try:
        print(f"Generating: \"{test_text}\"")
        success = voice.speak(test_text, output_file="test_voice_output.wav")

        if success:
            print("✅ Speech generated successfully!")
            print("   Saved to: test_voice_output.wav")
            print()
        else:
            print("❌ Speech generation failed")
            return False
    except Exception as e:
        print(f"❌ Error during speech generation: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Voice cloning test {'PASSED' if status['voice_cloning'] else 'PASSED (fallback mode)'}")
    print(f"   Mode: {status['tts_mode']}")
    print(f"   Reference samples: {status['reference_samples']}")
    print()

    if status['voice_cloning']:
        print("🎉 Your custom voice is ready to use!")
        print("   Try speaking with AiD using the voice_handler module.")
    else:
        print("💡 To enable voice cloning:")
        print("   1. Install Coqui TTS: pip install TTS sounddevice soundfile")
        print("   2. Add samples to voice_samples/reference/")
        print("   3. Run this test again")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_voice_cloning()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
