"""
Test Voice Cloning Functionality
Tests AiD's voice cloning capabilities using Coqui TTS XTTSv2
"""

import os
import sys
from pathlib import Path

def test_voice_cloning():
    """Test voice cloning setup and functionality."""

    print("\nStarting voice cloning test...\n")
    print("=" * 60)
    print("AiD Voice Cloning Test")
    print("=" * 60)

    # Step 1: Check for voice samples
    print("\n✓ Checking for voice samples...")
    voice_samples_dir = Path("voice_samples")

    if not voice_samples_dir.exists():
        print(f"❌ Voice samples directory not found: {voice_samples_dir}")
        print("   Please create 'voice_samples' directory with WAV files")
        return False

    voice_files = list(voice_samples_dir.glob("*.wav"))
    if not voice_files:
        print(f"❌ No WAV files found in {voice_samples_dir}")
        return False

    print(f"✓ Found {len(voice_files)} voice sample(s):")
    for i, voice_file in enumerate(voice_files, 1):
        size_mb = voice_file.stat().st_size / (1024 * 1024)
        print(f"  {i}. {voice_file.name} ({size_mb:.2f} MB)")

    # Step 2: Import voice handler
    print("\n[1/5] Importing voice handler...")
    try:
        import voice_handler
        print("✓ Voice handler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import voice_handler: {e}")
        return False

    # Step 3: Check dependencies
    print("\n[2/5] Checking dependencies...")

    # Check for Coqui TTS
    try:
        from TTS.api import TTS
        print("✓ Coqui TTS available")
    except ImportError:
        print("❌ Coqui TTS not installed")
        print("   Install with: pip install TTS")
        return False

    # Check transformers version for compatibility
    try:
        import transformers
        transformers_version = transformers.__version__
        print(f"✓ Transformers available (Version: {transformers_version})")

        # Fix transformers 4.50+ compatibility issue
        version_parts = transformers_version.split('.')
        major_minor = tuple(map(int, version_parts[:2]))
        if major_minor >= (4, 50):
            print(f"   ⚠️  Transformers {transformers_version} detected - applying compatibility patch...")

            # Patch GPT2InferenceModel to add the missing generate method
            try:
                from transformers import GenerationMixin
                from TTS.tts.layers.xtts.gpt import GPT2InferenceModel

                # Add GenerationMixin to GPT2InferenceModel's base classes if not present
                if GenerationMixin not in GPT2InferenceModel.__bases__:
                    GPT2InferenceModel.__bases__ = (GenerationMixin,) + GPT2InferenceModel.__bases__
                    print("   ✓ Applied transformers 4.50+ compatibility patch")
                else:
                    print("   ✓ GenerationMixin already present")
            except Exception as e:
                print(f"   ⚠️  Could not apply transformers patch: {e}")
                print("   ℹ️  Consider downgrading: pip install transformers==4.46.3")
    except ImportError:
        print("⚠️  Transformers not found - TTS may not work properly")
        print("   Install with: pip install transformers")

    # Check for PyTorch
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_version = torch.__version__
        print(f"✓ PyTorch available (Version: {torch_version}, Device: {device.upper()})")

        # Fix for PyTorch 2.6+ compatibility with Coqui TTS
        # PyTorch 2.6 changed torch.load to use weights_only=True by default
        # This breaks loading older TTS models, so we need to add safe globals
        pytorch_major_minor = tuple(map(int, torch_version.split('.')[:2]))
        if pytorch_major_minor >= (2, 6):
            print("   ⚠️  PyTorch 2.6+ detected - applying compatibility fix...")
            try:
                # Add TTS-related classes to safe globals for secure loading
                from TTS.tts.configs.xtts_config import XttsConfig
                from TTS.config import BaseAudioConfig, BaseDatasetConfig
                from coqpit import Coqpit

                # Import ALL XTTS model-specific classes
                safe_globals_list = [
                    XttsConfig,
                    BaseAudioConfig,
                    BaseDatasetConfig,
                    Coqpit,
                ]

                # Import all XTTS-related classes comprehensively
                try:
                    from TTS.tts.models.xtts import (
                        XttsAudioConfig,
                        XttsArgs,
                    )
                    safe_globals_list.extend([XttsAudioConfig, XttsArgs])
                except Exception as e:
                    print(f"   ⚠️  Could not import XTTS classes: {e}")

                # Try to import shared configs
                try:
                    from TTS.tts.configs.shared_configs import CharactersConfig
                    safe_globals_list.append(CharactersConfig)
                except:
                    pass

                # Add GPT and XTTS layers
                try:
                    from TTS.tts.layers.xtts.gpt import GPT
                    safe_globals_list.append(GPT)
                except:
                    pass

                # Add vocoder configs if needed
                try:
                    from TTS.vocoder.configs import HifiganConfig
                    safe_globals_list.append(HifiganConfig)
                except:
                    pass

                torch.serialization.add_safe_globals(safe_globals_list)
                print(f"   ✓ PyTorch 2.6 compatibility fix applied ({len(safe_globals_list)} classes registered)")
            except Exception as e:
                print(f"   ⚠️  Could not apply compatibility fix: {e}")
                print("   Continuing anyway...")

    except ImportError:
        print("❌ PyTorch not installed")
        print("   Install with: pip install torch")
        return False

    # Step 4: Initialize voice system (without bot parameter for standalone test)
    print("\n[3/5] Initializing TTS engine...")
    print("   Note: First run will download XTTSv2 model (~2GB)")
    print("   This may take a few minutes...")

    try:
        # Initialize the basic voice handler first
        voice_handler.init_voice()

        # Workaround for PyTorch 2.6+ if safe_globals didn't work
        # Temporarily patch torch.load to use weights_only=False for TTS model loading
        original_torch_load = None
        if pytorch_major_minor >= (2, 6):
            import functools
            original_torch_load = torch.load

            @functools.wraps(original_torch_load)
            def patched_load(*args, **kwargs):
                # Force weights_only=False for TTS model loading
                # This is safe because we trust Coqui TTS official models
                kwargs['weights_only'] = False
                return original_torch_load(*args, **kwargs)

            torch.load = patched_load
            print("   ⚠️  Applied torch.load patch for TTS compatibility")

        # Now try to initialize Coqui TTS for voice cloning
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

        # Restore original torch.load if we patched it
        if original_torch_load is not None:
            torch.load = original_torch_load
            print("   ✓ Restored original torch.load")

        if device == "cuda":
            tts = tts.to("cuda")

        print("✓ XTTSv2 model loaded successfully")

    except Exception as e:
        print(f"❌ Error initializing voice system: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 5: Test voice cloning
    print("\n[4/5] Testing voice cloning...")

    try:
        # Use the first voice sample
        sample_voice = str(voice_files[0])
        test_text = "Hello! I am AiD, testing my cloned voice. This is a test of the voice cloning system."
        output_file = "test_cloned_output.wav"

        print(f"   Using sample: {voice_files[0].name}")
        print(f"   Test text: {test_text[:50]}...")

        # Generate cloned voice
        tts.tts_to_file(
            text=test_text,
            file_path=output_file,
            speaker_wav=sample_voice,
            language="en"
        )

        if os.path.exists(output_file):
            size_kb = os.path.getsize(output_file) / 1024
            print(f"✓ Generated cloned voice: {output_file} ({size_kb:.2f} KB)")
        else:
            print("❌ Output file was not created")
            return False

    except Exception as e:
        print(f"❌ Error during voice cloning: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Summary
    print("\n[5/5] Test Summary")
    print("=" * 60)
    print("✅ All tests passed successfully!")
    print("\nVoice cloning is working correctly:")
    print(f"  • Model: XTTSv2")
    print(f"  • Device: {device.upper()}")
    print(f"  • Voice samples: {len(voice_files)}")
    print(f"  • Test output: {output_file}")
    print("\nNext steps:")
    print("  1. Listen to the generated file to verify quality")
    print("  2. Try with different voice samples")
    print("  3. Integrate with bot.py for Discord usage")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_voice_cloning()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
