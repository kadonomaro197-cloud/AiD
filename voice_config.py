"""
Voice Configuration for AiD TTS
Adjust these parameters to fine-tune speech quality, pacing, and naturalness.
"""

class VoiceConfig:
    """
    Configuration for Coqui XTTS v2 voice synthesis.

    Adjust these parameters to control:
    - Speech clarity and consistency
    - Pacing and pauses
    - Naturalness vs stability
    """

    # ============================================================
    # SPEECH QUALITY PARAMETERS
    # ============================================================

    # Temperature: Controls randomness/creativity
    # - Lower (0.1-0.5): More consistent, less natural, reduces slurring
    # - Medium (0.5-0.7): Balanced (RECOMMENDED)
    # - Higher (0.7-1.0): More expressive but less consistent
    TEMPERATURE = 0.65

    # Repetition Penalty: Reduces repetitive patterns
    # - Lower (1.0-2.0): May repeat sounds/words
    # - Medium (2.0-5.0): Balanced (RECOMMENDED)
    # - Higher (5.0-10.0): Avoids repetition aggressively
    REPETITION_PENALTY = 2.5

    # Length Penalty: Affects speech duration and pacing
    # - Lower (0.5-1.0): Faster, shorter pauses
    # - Default (1.0): Natural pacing
    # - Higher (1.0-2.0): Slower, longer pauses
    LENGTH_PENALTY = 1.0

    # ============================================================
    # SAMPLING PARAMETERS
    # ============================================================

    # Top-K Sampling: Limits vocabulary choices
    # - Lower (10-30): More predictable, clearer
    # - Medium (50): Balanced (RECOMMENDED)
    # - Higher (100+): More varied but potentially unclear
    TOP_K = 50

    # Top-P (Nucleus Sampling): Probability threshold
    # - Lower (0.7-0.85): More focused, clearer
    # - Medium (0.85-0.9): Balanced (RECOMMENDED)
    # - Higher (0.9-1.0): More creative but less stable
    TOP_P = 0.85

    # ============================================================
    # TEXT PROCESSING
    # ============================================================

    # Enable Text Splitting: Split long text into sentences
    # - True: Better for long passages, more natural pauses
    # - False: Better for short phrases, less pausing
    ENABLE_TEXT_SPLITTING = True

    # Speed: Speech rate multiplier (if supported by model)
    # - 0.5-0.9: Slower, more deliberate
    # - 1.0: Normal speed
    # - 1.1-1.5: Faster, more energetic
    # Note: Not all XTTS versions support this parameter
    SPEED = 1.0

    # ============================================================
    # REFERENCE AUDIO SELECTION
    # ============================================================

    # Which reference sample to use (0 = first, -1 = random)
    # You can cycle through different emotional samples
    REFERENCE_SAMPLE_INDEX = 0

    # ============================================================
    # PRESETS - Quick configurations
    # ============================================================

    @classmethod
    def preset_clear_and_stable(cls):
        """Clear speech, minimal slurring, consistent delivery."""
        cls.TEMPERATURE = 0.45
        cls.REPETITION_PENALTY = 4.0
        cls.LENGTH_PENALTY = 1.0
        cls.TOP_K = 30
        cls.TOP_P = 0.8
        cls.ENABLE_TEXT_SPLITTING = True

    @classmethod
    def preset_natural_and_expressive(cls):
        """More natural, expressive, but may have slight variations."""
        cls.TEMPERATURE = 0.75
        cls.REPETITION_PENALTY = 2.0
        cls.LENGTH_PENALTY = 1.0
        cls.TOP_K = 70
        cls.TOP_P = 0.9
        cls.ENABLE_TEXT_SPLITTING = True

    @classmethod
    def preset_fast_paced(cls):
        """Faster speech with shorter pauses."""
        cls.TEMPERATURE = 0.60
        cls.REPETITION_PENALTY = 3.0
        cls.LENGTH_PENALTY = 0.8
        cls.TOP_K = 50
        cls.TOP_P = 0.85
        cls.ENABLE_TEXT_SPLITTING = False
        cls.SPEED = 1.15

    @classmethod
    def preset_slow_and_deliberate(cls):
        """Slower, more thoughtful delivery."""
        cls.TEMPERATURE = 0.55
        cls.REPETITION_PENALTY = 2.5
        cls.LENGTH_PENALTY = 1.3
        cls.TOP_K = 40
        cls.TOP_P = 0.82
        cls.ENABLE_TEXT_SPLITTING = True
        cls.SPEED = 0.90

    @classmethod
    def reset_to_defaults(cls):
        """Reset all values to recommended defaults."""
        cls.TEMPERATURE = 0.65
        cls.REPETITION_PENALTY = 2.5
        cls.LENGTH_PENALTY = 1.0
        cls.TOP_K = 50
        cls.TOP_P = 0.85
        cls.ENABLE_TEXT_SPLITTING = True
        cls.SPEED = 1.0
        cls.REFERENCE_SAMPLE_INDEX = 0


# ============================================================
# TROUBLESHOOTING GUIDE
# ============================================================

"""
PROBLEM: Speech sounds slurred or mumbly
SOLUTION:
  - Lower TEMPERATURE (try 0.45-0.55)
  - Increase REPETITION_PENALTY (try 3.5-4.5)
  - Lower TOP_P (try 0.75-0.80)
  - Or use: VoiceConfig.preset_clear_and_stable()

PROBLEM: Pauses are too long
SOLUTION:
  - Lower LENGTH_PENALTY (try 0.7-0.9)
  - Set ENABLE_TEXT_SPLITTING = False
  - Or use: VoiceConfig.preset_fast_paced()

PROBLEM: Speech sounds robotic or unnatural
SOLUTION:
  - Increase TEMPERATURE (try 0.70-0.80)
  - Lower REPETITION_PENALTY (try 2.0-2.5)
  - Increase TOP_P (try 0.88-0.92)
  - Or use: VoiceConfig.preset_natural_and_expressive()

PROBLEM: Words/sounds repeat
SOLUTION:
  - Increase REPETITION_PENALTY (try 4.0-6.0)
  - Lower TEMPERATURE (try 0.50-0.60)

PROBLEM: Speech is too fast
SOLUTION:
  - Increase LENGTH_PENALTY (try 1.2-1.4)
  - Lower SPEED (try 0.85-0.95)
  - Or use: VoiceConfig.preset_slow_and_deliberate()

PROBLEM: Speech is too slow
SOLUTION:
  - Lower LENGTH_PENALTY (try 0.8-0.9)
  - Increase SPEED (try 1.1-1.3)
  - Or use: VoiceConfig.preset_fast_paced()

PROBLEM: Voice doesn't match samples
SOLUTION:
  - Check sample quality with: python check_voice_samples.py
  - Try different REFERENCE_SAMPLE_INDEX (0-16 for your 17 samples)
  - Ensure samples are clean, 10-20 seconds, mono, 22050 Hz
"""
