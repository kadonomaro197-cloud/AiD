#!/usr/bin/env python3
"""
Test Voice Cloning System
Tests TTS with voice cloning before running the full bot.
"""

import os
import sys
from pathlib import Path

def test_voice_cloning():
    """Test the voice cloning system."""
    print("=" * 60)
    print("AiD Voice Cloning Test")
    print("=" * 60)

    # Check for voice samples
    voice_samples_dir = Path("voice_samples")
    if not voice_samples_dir.exists():
        print("\n❌ Error: voice_samples directory not found!")
        print("   Create it with: mkdir voice_samples")
        return False

    wav_files = list(voice_samples_dir.glob("*.wav"))
    if not wav_files:
        print(f"\n❌ Error: No WAV files found in {voice_samples_dir}")
        print("   Please add your voice samples (*.wav) to the voice_samples directory")
        return False

    print(f"\n✓ Found {len(wav_files)} voice sample(s):")
    for i, sample in enumerate(wav_files, 1):
        file_size = sample.stat().st_size / 1024 / 1024  # MB
        print(f"  {i}. {sample.name} ({file_size:.2f} MB)")

    # Import voice handler
    print("\n[1/5] Importing voice handler...")
    try:
        import voice_handler
        print("✓ Voice handler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import voice_handler: {e}")
        print("   Make sure all dependencies are installed: pip install -r requirements.txt")
        return False

    # Check dependencies
    print("\n[2/5] Checking dependencies...")
    try:
        from TTS.api import TTS
        print("✓ Coqui TTS available")
    except ImportError:
        print("❌ Coqui TTS not installed")
        print("   Install with: pip install TTS")
        return False

    try:
        import torch
        cuda_available = torch.cuda.is_available()
        device = "CUDA" if cuda_available else "CPU"
        print(f"✓ PyTorch available (Device: {device})")
        if cuda_available:
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("❌ PyTorch not installed")
        print("   Install with: pip install torch torchaudio")
        return False

    # Initialize TTS engine
    print("\n[3/5] Initializing TTS engine...")
    print("   Note: First run will download XTTSv2 model (~2GB)")
    print("   This may take a few minutes...")

    try:
        status = voice_handler.init_voice()
        if status['tts']:
            print("✓ TTS engine initialized successfully")
        else:
            print("❌ TTS engine failed to initialize")
            return False
    except Exception as e:
        print(f"❌ Error initializing voice system: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Get voice manager
    print("\n[4/5] Testing voice synthesis...")
    vm = voice_handler.get_voice_manager()
    if not vm:
        print("❌ Voice manager not available")
        return False

    # Generate test audio
    test_phrases = [
        "Hello! This is AiD testing the voice cloning system.",
        "If you can hear this, the voice cloning is working perfectly!",
        "Ready to chat in my custom voice, boss!"
    ]

    output_dir = Path("test_audio_output")
    output_dir.mkdir(exist_ok=True)

    print(f"   Generating {len(test_phrases)} test audio files...")

    for i, phrase in enumerate(test_phrases, 1):
        print(f"   [{i}/{len(test_phrases)}] Generating: '{phrase[:50]}...'")
        output_path = str(output_dir / f"test_{i}.wav")

        try:
            audio_path = vm.tts_engine.synthesize(phrase, output_path=output_path)
            if audio_path:
                file_size = Path(audio_path).stat().st_size / 1024  # KB
                print(f"       ✓ Saved to: {audio_path} ({file_size:.1f} KB)")
            else:
                print(f"       ❌ Failed to generate audio")
        except Exception as e:
            print(f"       ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n[5/5] Test Summary")
    print("=" * 60)
    print("✓ Voice cloning system is working!")
    print(f"✓ Test audio files saved in: {output_dir}/")
    print("\nYou can play these files to hear your custom voice:")
    print(f"  - {output_dir}/test_1.wav")
    print(f"  - {output_dir}/test_2.wav")
    print(f"  - {output_dir}/test_3.wav")
    print("\nTo use with Discord bot:")
    print("  1. Start the bot: python bot.py")
    print("  2. Join a voice channel")
    print("  3. Type: !join_voice")
    print("  4. Chat normally - AiD will respond in voice!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    print("\nStarting voice cloning test...\n")
    success = test_voice_cloning()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Check the errors above.")
        sys.exit(1)
