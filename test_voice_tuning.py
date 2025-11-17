"""
Voice Tuning Test Script
Test different voice configurations to find the perfect settings.
"""

import sys
from voice_config import VoiceConfig
from voice_handler import get_voice

# Test phrase
TEST_PHRASE = "Hello! I am AiD, your advanced intelligence assistant. How can I help you today?"

def test_current_config():
    """Test with current configuration."""
    print("\n" + "=" * 60)
    print("Testing CURRENT CONFIGURATION")
    print("=" * 60)
    print(f"Temperature: {VoiceConfig.TEMPERATURE}")
    print(f"Repetition Penalty: {VoiceConfig.REPETITION_PENALTY}")
    print(f"Length Penalty: {VoiceConfig.LENGTH_PENALTY}")
    print(f"Top-K: {VoiceConfig.TOP_K}")
    print(f"Top-P: {VoiceConfig.TOP_P}")
    print(f"Text Splitting: {VoiceConfig.ENABLE_TEXT_SPLITTING}")
    print(f"Speed: {VoiceConfig.SPEED}")
    print(f"Reference Sample: {VoiceConfig.REFERENCE_SAMPLE_INDEX}")
    print("=" * 60)

    voice = get_voice()
    print(f"\nGenerating: '{TEST_PHRASE}'")
    voice.speak(TEST_PHRASE, output_file="test_current_config.wav")
    print("✅ Saved to: test_current_config.wav")

def test_preset(preset_name, preset_func):
    """Test a preset configuration."""
    print("\n" + "=" * 60)
    print(f"Testing PRESET: {preset_name}")
    print("=" * 60)

    # Apply preset
    preset_func()

    print(f"Temperature: {VoiceConfig.TEMPERATURE}")
    print(f"Repetition Penalty: {VoiceConfig.REPETITION_PENALTY}")
    print(f"Length Penalty: {VoiceConfig.LENGTH_PENALTY}")
    print(f"Top-K: {VoiceConfig.TOP_K}")
    print(f"Top-P: {VoiceConfig.TOP_P}")
    print(f"Text Splitting: {VoiceConfig.ENABLE_TEXT_SPLITTING}")
    print(f"Speed: {VoiceConfig.SPEED}")
    print("=" * 60)

    voice = get_voice()
    output_file = f"test_{preset_name.lower().replace(' ', '_')}.wav"
    print(f"\nGenerating: '{TEST_PHRASE}'")
    voice.speak(TEST_PHRASE, output_file=output_file)
    print(f"✅ Saved to: {output_file}")

    # Reset to defaults after test
    VoiceConfig.reset_to_defaults()

def test_all_presets():
    """Test all available presets."""
    presets = [
        ("Clear and Stable", VoiceConfig.preset_clear_and_stable),
        ("Natural and Expressive", VoiceConfig.preset_natural_and_expressive),
        ("Fast Paced", VoiceConfig.preset_fast_paced),
        ("Slow and Deliberate", VoiceConfig.preset_slow_and_deliberate),
    ]

    for name, func in presets:
        test_preset(name, func)

    print("\n" + "=" * 60)
    print("✅ ALL PRESETS TESTED!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - test_clear_and_stable.wav")
    print("  - test_natural_and_expressive.wav")
    print("  - test_fast_paced.wav")
    print("  - test_slow_and_deliberate.wav")
    print("\nListen to each file and choose the one you prefer!")
    print("Then edit voice_config.py to use that preset or adjust manually.")

def test_custom_phrase(phrase):
    """Test with a custom phrase."""
    print("\n" + "=" * 60)
    print("Testing CUSTOM PHRASE")
    print("=" * 60)
    print(f"Phrase: '{phrase}'")
    print("=" * 60)

    voice = get_voice()
    voice.speak(phrase, output_file="test_custom_phrase.wav")
    print("✅ Saved to: test_custom_phrase.wav")

def show_help():
    """Show usage instructions."""
    print("=" * 60)
    print("AiD Voice Tuning Test Script")
    print("=" * 60)
    print("\nUsage:")
    print("  python test_voice_tuning.py                 - Test current config")
    print("  python test_voice_tuning.py all             - Test all presets")
    print("  python test_voice_tuning.py clear           - Test 'Clear and Stable'")
    print("  python test_voice_tuning.py natural         - Test 'Natural and Expressive'")
    print("  python test_voice_tuning.py fast            - Test 'Fast Paced'")
    print("  python test_voice_tuning.py slow            - Test 'Slow and Deliberate'")
    print('  python test_voice_tuning.py "Custom text"   - Test custom phrase')
    print("\nAfter testing:")
    print("  1. Listen to the generated .wav files")
    print("  2. Choose your favorite settings")
    print("  3. Edit voice_config.py to apply permanently")
    print("\nTroubleshooting:")
    print("  - See voice_config.py for parameter explanations")
    print("  - See bottom of voice_config.py for problem-solving guide")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - test current config
        test_current_config()
    elif sys.argv[1] == "help" or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        show_help()
    elif sys.argv[1] == "all":
        test_all_presets()
    elif sys.argv[1] == "clear":
        test_preset("Clear and Stable", VoiceConfig.preset_clear_and_stable)
    elif sys.argv[1] == "natural":
        test_preset("Natural and Expressive", VoiceConfig.preset_natural_and_expressive)
    elif sys.argv[1] == "fast":
        test_preset("Fast Paced", VoiceConfig.preset_fast_paced)
    elif sys.argv[1] == "slow":
        test_preset("Slow and Deliberate", VoiceConfig.preset_slow_and_deliberate)
    else:
        # Treat as custom phrase
        phrase = " ".join(sys.argv[1:])
        test_custom_phrase(phrase)
