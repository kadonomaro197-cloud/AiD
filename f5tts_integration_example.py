#!/usr/bin/env python3
"""
F5-TTS Integration Example for Two-Stage Voice Cloning

This script demonstrates how to integrate F5-TTS (recommended Stage 1 tool)
with the AiD two-stage voice cloning pipeline.

Prerequisites:
    1. Install F5-TTS:
       git clone https://github.com/SWivid/F5-TTS.git
       cd F5-TTS
       pip install -r requirements.txt

    2. Ensure F5-TTS is in your Python path or installed as a package

Usage:
    python f5tts_integration_example.py <original_sample.wav> [num_samples]

Example:
    python f5tts_integration_example.py my_voice.wav 5
"""

import os
import sys
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path


class F5TTSTwoStagePipeline:
    """Two-stage pipeline using F5-TTS for Stage 1 generation"""

    def __init__(self, original_sample_path):
        self.original_sample = Path(original_sample_path)
        self.output_dir = Path("/home/user/AiD/voice_samples")
        self.temp_dir = Path("/tmp/two_stage_voice")

        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

        # Verify original sample
        if not self.original_sample.exists():
            raise FileNotFoundError(f"Original sample not found: {self.original_sample}")

        # Initialize F5-TTS model
        self.init_f5tts()

        print(f"✅ Initialized F5-TTS pipeline")
        print(f"   Original: {self.original_sample}")
        print(f"   Output dir: {self.output_dir}")

    def init_f5tts(self):
        """Initialize F5-TTS model"""
        print("🔄 Initializing F5-TTS model...")

        try:
            # NOTE: This is pseudo-code. Adjust based on actual F5-TTS API
            # Uncomment and modify when F5-TTS is installed:

            # from f5_tts import F5TTS
            # self.tts_model = F5TTS()
            # print("   ✅ F5-TTS model loaded")

            # For now, set to None to indicate placeholder mode
            self.tts_model = None
            print("   ⚠️  F5-TTS not available - using placeholder mode")
            print("   ℹ️  Install F5-TTS to enable real voice generation")

        except ImportError as e:
            print(f"   ⚠️  F5-TTS import failed: {e}")
            print("   ℹ️  Using placeholder mode")
            self.tts_model = None

    def generate_varied_scripts(self, count=5):
        """Generate varied text scripts for diversity"""
        scripts = [
            "The quick brown fox jumps over the lazy dog with enthusiasm and energy.",
            "How are you doing today? I hope everything is going well for you!",
            "This sample demonstrates a calm and measured speaking tone for clarity.",
            "Let's include some excitement and energy in our voice! This is great!",
            "Reading naturally with varied pitch and rhythm patterns works best.",
            "Sometimes we need to express curiosity. What do you think about this?",
            "A gentle, soothing tone can be useful for certain applications too.",
            "Technical information should be delivered clearly and precisely.",
            "Expressive speech with emotion makes the voice sound more natural!",
            "Finally, we'll end with a balanced and neutral tone for variety."
        ]
        return scripts[:count]

    def stage1_generate_with_f5tts(self, text, output_path):
        """
        Stage 1: Generate using F5-TTS

        Parameters:
            text: Text to synthesize
            output_path: Where to save generated audio

        Quality settings optimized for AiD requirements:
            - Sample rate: 22050 Hz (AiD optimal)
            - Channels: 1 (mono)
            - Bit depth: 16-bit
            - Normalization: Enabled
            - Silence removal: Enabled
        """
        print(f"   🎤 Stage 1: F5-TTS generation...")
        print(f"      Text: \"{text[:60]}...\"")

        if self.tts_model is not None:
            # REAL F5-TTS GENERATION
            # Uncomment and modify based on actual F5-TTS API:

            """
            try:
                self.tts_model.clone_voice(
                    reference_audio=str(self.original_sample),
                    text=text,
                    output_path=str(output_path),

                    # Quality settings for AiD compatibility
                    sample_rate=22050,      # AiD optimal
                    channels=1,              # Mono only
                    bit_depth=16,            # Standard quality
                    normalize=True,          # Consistent volume
                    remove_silence=True,     # Clean edges
                    peak_limit=0.90,         # Prevent clipping
                    rms_target=0.15,         # Good volume level

                    # F5-TTS specific settings
                    speed=1.0,               # Normal speed
                    temperature=0.7,         # Creativity level
                    top_p=0.9,               # Sampling parameter
                )
                print(f"      ✓ F5-TTS generated: {output_path}")

            except Exception as e:
                print(f"      ❌ F5-TTS generation failed: {e}")
                # Fallback to placeholder
                self._placeholder_generate(output_path)
            """

            # For now, use placeholder
            self._placeholder_generate(output_path)

        else:
            # PLACEHOLDER MODE
            self._placeholder_generate(output_path)

    def _placeholder_generate(self, output_path):
        """Placeholder generation (copy original sample)"""
        print(f"      ⚠️  PLACEHOLDER: Copying original sample")
        print(f"      ℹ️  Install F5-TTS for real generation")

        # Load and save original to create new file
        audio, sr = librosa.load(str(self.original_sample), sr=None, mono=False)
        sf.write(str(output_path), audio, sr)

        print(f"      ✓ Placeholder generated: {output_path}")

    def check_audio_quality(self, audio, sr):
        """Check audio quality metrics"""
        rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        duration = len(audio) / sr

        return {
            'rms': rms,
            'peak': peak,
            'duration': duration
        }

    def stage2_post_process(self, input_file, output_file, sample_number):
        """
        Stage 2: Post-process to match AiD requirements

        Ensures output meets all AiD specifications:
        - Format: WAV
        - Sample rate: 22050 Hz
        - Channels: Mono (1)
        - Bit depth: 16-bit
        - Duration: 6-30 seconds
        - RMS: >= 0.05
        - Peak: < 0.95
        """
        print(f"\n   ⚙️  Stage 2: Post-processing sample {sample_number}...")

        # Load as mono, 22050 Hz
        audio, sr = librosa.load(str(input_file), sr=22050, mono=True)

        # Initial quality check
        initial_quality = self.check_audio_quality(audio, sr)
        print(f"      📊 Initial - Duration: {initial_quality['duration']:.1f}s, "
              f"RMS: {initial_quality['rms']:.3f}, Peak: {initial_quality['peak']:.3f}")

        # Trim silence from edges (top_db=30 means remove parts quieter than -30dB)
        audio, _ = librosa.effects.trim(audio, top_db=30)

        # Normalize peak to 0.90 (safely below 0.95 clipping threshold)
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.90

        # Check and fix RMS (minimum 0.05)
        rms = np.sqrt(np.mean(audio**2))
        if rms < 0.05:
            target_rms = 0.15
            audio = audio * (target_rms / rms) if rms > 0 else audio
            print(f"      🔊 Amplified: RMS {rms:.3f} -> {target_rms:.3f}")

        # Check duration (6-30 seconds optimal)
        duration = len(audio) / sr
        if duration < 6:
            print(f"      ⚠️  WARNING: Duration {duration:.1f}s is below 6s minimum!")
        elif duration > 30:
            audio = audio[:25*sr]
            print(f"      ✂️  Trimmed: {duration:.1f}s -> 25.0s")

        # Final quality check
        final_quality = self.check_audio_quality(audio, sr)

        # Save as 16-bit WAV, mono, 22050 Hz
        sf.write(str(output_file), audio, 22050, subtype='PCM_16')

        print(f"      ✅ Final - Duration: {final_quality['duration']:.1f}s, "
              f"RMS: {final_quality['rms']:.3f}, Peak: {final_quality['peak']:.3f}")
        print(f"      💾 Saved: {output_file.name}")

        return final_quality

    def run_pipeline(self, num_samples=5):
        """Execute complete two-stage pipeline with F5-TTS"""
        print("\n" + "=" * 70)
        print(" F5-TTS TWO-STAGE VOICE CLONING PIPELINE")
        print("=" * 70)
        print(f"\n📁 Configuration:")
        print(f"   Original sample: {self.original_sample}")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Number of samples: {num_samples}")
        print(f"   Stage 1 tool: F5-TTS ({'ACTIVE' if self.tts_model else 'PLACEHOLDER'})")
        print(f"\n🎯 Target specifications:")
        print(f"   Format: WAV, 22050 Hz, Mono, 16-bit")
        print(f"   Duration: 6-30 seconds (optimal: 10-20s)")
        print(f"   RMS: >= 0.05, Peak: < 0.95")
        print(f"\n" + "-" * 70)

        # Generate scripts
        scripts = self.generate_varied_scripts(num_samples)

        # Process each sample
        quality_summary = []

        for i, script in enumerate(scripts, 1):
            print(f"\n[{i}/{num_samples}] PROCESSING SAMPLE {i}")
            print(f"{'─' * 70}")
            print(f"📝 Script: \"{script}\"")

            # Stage 1: Generate with F5-TTS
            temp_file = self.temp_dir / f"f5tts_stage1_{i}.wav"
            self.stage1_generate_with_f5tts(script, temp_file)

            # Stage 2: Post-process for AiD
            final_file = self.output_dir / f"AiD Voice Sample {i}.wav"
            quality = self.stage2_post_process(temp_file, final_file, i)
            quality_summary.append((i, quality))

            # Cleanup temp file
            if temp_file.exists():
                temp_file.unlink()

        # Final summary
        print(f"\n" + "=" * 70)
        print(" PIPELINE COMPLETE")
        print("=" * 70)
        print(f"\n✅ Generated {num_samples} samples in: {self.output_dir}")

        print(f"\n📊 Quality Summary:")
        print(f"{'─' * 70}")
        print(f"{'Sample':<10} {'Duration':<12} {'RMS':<10} {'Peak':<10} {'Status'}")
        print(f"{'─' * 70}")

        for sample_num, quality in quality_summary:
            status = "✅ Good"
            if quality['duration'] < 6 or quality['duration'] > 30:
                status = "⚠️  Duration"
            elif quality['rms'] < 0.05:
                status = "⚠️  Quiet"
            elif quality['peak'] > 0.95:
                status = "⚠️  Loud"

            print(f"{sample_num:<10} {quality['duration']:<12.1f} "
                  f"{quality['rms']:<10.3f} {quality['peak']:<10.3f} {status}")

        print(f"{'─' * 70}")

        # Next steps
        print(f"\n📋 Next Steps:")
        print(f"   1. Validate samples:")
        print(f"      → python check_voice_samples.py")
        print(f"\n   2. Review quality scores (target: 60+ points)")
        print(f"\n   3. Test voice cloning:")
        print(f"      → python test_voice_cloning.py")

        if not self.tts_model:
            print(f"\n⚠️  IMPORTANT: F5-TTS not active - using placeholder!")
            print(f"   To enable F5-TTS:")
            print(f"   1. git clone https://github.com/SWivid/F5-TTS.git")
            print(f"   2. cd F5-TTS && pip install -r requirements.txt")
            print(f"   3. Update init_f5tts() method with correct API calls")

        print(f"\n" + "=" * 70 + "\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print(" F5-TTS Two-Stage Voice Cloning Pipeline")
        print("=" * 70)
        print("\nUsage:")
        print("  python f5tts_integration_example.py <original_sample.wav> [num_samples]")
        print("\nExample:")
        print("  python f5tts_integration_example.py my_voice.wav 5")
        print("\nPrerequisites:")
        print("  1. Install F5-TTS:")
        print("     git clone https://github.com/SWivid/F5-TTS.git")
        print("     cd F5-TTS && pip install -r requirements.txt")
        print("\nArguments:")
        print("  original_sample.wav  - Path to original voice sample")
        print("  num_samples         - Number of samples to generate (default: 5)")
        print("\nOutput:")
        print("  Samples saved to: /home/user/AiD/voice_samples/")
        print("=" * 70)
        sys.exit(1)

    # Get arguments
    original_sample = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    # Validate
    if not os.path.exists(original_sample):
        print(f"❌ Error: File not found: {original_sample}")
        sys.exit(1)

    if num_samples < 1 or num_samples > 20:
        print(f"❌ Error: num_samples must be between 1 and 20")
        sys.exit(1)

    # Check dependencies
    try:
        import librosa
        import soundfile as sf
        import numpy as np
    except ImportError as e:
        print(f"❌ Error: Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  pip install librosa soundfile numpy")
        sys.exit(1)

    # Run pipeline
    try:
        pipeline = F5TTSTwoStagePipeline(original_sample)
        pipeline.run_pipeline(num_samples=num_samples)
    except Exception as e:
        print(f"\n❌ Error: Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
