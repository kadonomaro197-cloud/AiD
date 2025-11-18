"""
Voice Configuration for AiD TTS
Adjust these parameters to fine-tune speech quality, pacing, and naturalness.

CURRENT CONFIGURATION: Accent Emphasis
- Optimized to bring out strong accent characteristics
- High expressiveness (TEMP=0.82, TOP_P=0.94)
- Lower repetition penalty to allow accent patterns
- Try different REFERENCE_SAMPLE_INDEX (0-16) to find samples with strongest accent
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
    # ACCENT EMPHASIS: Set higher for stronger accent (0.82)
    TEMPERATURE = 0.82

    # Repetition Penalty: Reduces repetitive patterns
    # - Lower (1.0-2.0): May repeat sounds/words
    # - Medium (2.0-5.0): Balanced (RECOMMENDED)
    # - Higher (5.0-10.0): Avoids repetition aggressively
    # ACCENT EMPHASIS: Set lower to allow accent patterns (1.8)
    REPETITION_PENALTY = 1.8

    # Length Penalty: Affects speech duration and pacing
    # - Lower (0.5-1.0): Faster, shorter pauses
    # - Default (1.0): Natural pacing
    # - Higher (1.0-2.0): Slower, longer pauses
    # ACCENT EMPHASIS: Slightly higher for deliberate accent (1.2)
    LENGTH_PENALTY = 1.2

    # ============================================================
    # SAMPLING PARAMETERS
    # ============================================================

    # Top-K Sampling: Limits vocabulary choices
    # - Lower (10-30): More predictable, clearer
    # - Medium (50): Balanced (RECOMMENDED)
    # - Higher (100+): More varied but potentially unclear
    # ACCENT EMPHASIS: Higher for accent pronunciation variety (90)
    TOP_K = 90

    # Top-P (Nucleus Sampling): Probability threshold
    # - Lower (0.7-0.85): More focused, clearer
    # - Medium (0.85-0.9): Balanced (RECOMMENDED)
    # - Higher (0.9-1.0): More creative but less stable
    # ACCENT EMPHASIS: Higher for diverse accent patterns (0.94)
    TOP_P = 0.94

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
    # ACCENT EMPHASIS: Slightly slower for clear accent (0.92)
    SPEED = 0.92

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
    def preset_accent_emphasis(cls):
        """Emphasize accent characteristics with high expressiveness."""
        cls.TEMPERATURE = 0.82
        cls.REPETITION_PENALTY = 1.8
        cls.LENGTH_PENALTY = 1.2
        cls.TOP_K = 90
        cls.TOP_P = 0.94
        cls.ENABLE_TEXT_SPLITTING = True
        cls.SPEED = 0.92

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

PROBLEM: Accent is too weak or not coming through
SOLUTION:
  - Increase TEMPERATURE (try 0.78-0.85) - allows more accent variation
  - Increase TOP_P (try 0.92-0.95) - enables more diverse speech patterns
  - Increase TOP_K (try 85-100) - more pronunciation choices
  - Lower REPETITION_PENALTY (try 1.5-2.0) - allows accent patterns to repeat
  - CRITICAL: Try different REFERENCE_SAMPLE_INDEX - some samples have stronger accents
  - Or use: VoiceConfig.preset_accent_emphasis()
"""