#!/usr/bin/env python3
"""
Two-Stage Voice Cloning Pipeline
Generates high-quality samples for AiD voice cloning

Usage:
    python generate_two_stage_samples.py <original_voice_sample.wav> [num_samples]

Example:
    python generate_two_stage_samples.py my_voice.wav 5
"""

import os
import sys
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path


class TwoStageVoicePipeline:
    """Two-stage voice cloning pipeline for AiD"""

    def __init__(self, original_sample_path):
        self.original_sample = Path(original_sample_path)
        self.output_dir = Path("/home/user/AiD/voice_samples")
        self.temp_dir = Path("/tmp/two_stage_voice")

        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

        # Verify original sample exists
        if not self.original_sample.exists():
            raise FileNotFoundError(f"Original sample not found: {self.original_sample}")

        print(f"✅ Initialized pipeline")
        print(f"   Original: {self.original_sample}")
        print(f"   Output dir: {self.output_dir}")

    def generate_varied_scripts(self, count=5):
        """
        Generate varied text scripts for diversity

        These scripts are designed to:
        - Cover different speaking styles
        - Include varied intonation patterns
        - Test different emotional ranges
        - Ensure phonetic diversity
        """
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

    def stage1_generate_placeholder(self, text, output_path):
        """
        Stage 1: Generate using external TTS (PLACEHOLDER)

        THIS IS A PLACEHOLDER - Replace with your chosen TTS tool:
        - F5-TTS (recommended)
        - StyleTTS2
        - RVC
        - Other voice cloning software

        For now, this creates a copy of the original with metadata
        for demonstration purposes.
        """
        print(f"   🎤 Stage 1: Generating sample...")
        print(f"      Text: \"{text[:60]}...\"")

        # PLACEHOLDER: Copy original sample
        # In real usage, replace this with actual TTS generation
        print(f"      ⚠️  PLACEHOLDER MODE: Copying original sample")
        print(f"      ℹ️  Replace this with F5-TTS/StyleTTS2/RVC generation")

        # Load and save to create a new file
        audio, sr = librosa.load(str(self.original_sample), sr=None, mono=False)
        sf.write(output_path, audio, sr)

        print(f"      ✓ Generated: {output_path}")

    def check_audio_quality(self, audio, sr):
        """Check audio quality metrics"""
        # Calculate RMS
        rms = np.sqrt(np.mean(audio**2))

        # Calculate peak
        peak = np.max(np.abs(audio))

        # Calculate duration
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

        # Trim silence from edges
        audio, _ = librosa.effects.trim(audio, top_db=30)

        # Normalize peak to 0.90 (safely below 0.95 clipping threshold)
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.90
        else:
            print(f"      ⚠️  WARNING: Audio is silent!")

        # Check and fix RMS (minimum 0.05)
        rms = np.sqrt(np.mean(audio**2))
        if rms < 0.05:
            target_rms = 0.15  # Good target level
            audio = audio * (target_rms / rms) if rms > 0 else audio
            print(f"      🔊 Amplified: RMS {rms:.3f} -> {target_rms:.3f}")

        # Check duration (6-30 seconds optimal)
        duration = len(audio) / sr
        if duration < 6:
            print(f"      ⚠️  WARNING: Duration {duration:.1f}s is below 6s minimum!")
            print(f"         Consider using longer text in Stage 1")
        elif duration > 30:
            # Trim to 25 seconds
            audio = audio[:25*sr]
            print(f"      ✂️  Trimmed: {duration:.1f}s -> 25.0s")
            duration = 25.0

        # Final quality check
        final_quality = self.check_audio_quality(audio, sr)

        # Save as 16-bit WAV, mono, 22050 Hz
        sf.write(str(output_file), audio, 22050, subtype='PCM_16')

        # Report
        print(f"      ✅ Final - Duration: {final_quality['duration']:.1f}s, "
              f"RMS: {final_quality['rms']:.3f}, Peak: {final_quality['peak']:.3f}")
        print(f"      💾 Saved: {output_file.name}")

        # Quality warnings
        warnings = []
        if final_quality['duration'] < 6:
            warnings.append("Duration too short")
        if final_quality['duration'] > 30:
            warnings.append("Duration too long")
        if final_quality['rms'] < 0.05:
            warnings.append("RMS too low")
        if final_quality['peak'] > 0.95:
            warnings.append("May clip")

        if warnings:
            print(f"      ⚠️  Warnings: {', '.join(warnings)}")

        return final_quality

    def run_pipeline(self, num_samples=5):
        """Execute complete two-stage pipeline"""
        print("\n" + "=" * 70)
        print(" TWO-STAGE VOICE CLONING PIPELINE FOR AiD")
        print("=" * 70)
        print(f"\n📁 Configuration:")
        print(f"   Original sample: {self.original_sample}")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Number of samples: {num_samples}")
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

            # Stage 1: Generate with external TTS
            temp_file = self.temp_dir / f"stage1_temp_{i}.wav"
            self.stage1_generate_placeholder(script, temp_file)

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
        print(f"   1. Run quality checker:")
        print(f"      → python check_voice_samples.py")
        print(f"\n   2. Review quality scores (target: 60+ points)")
        print(f"\n   3. Test voice cloning:")
        print(f"      → python test_voice_cloning.py")
        print(f"\n   4. If quality < 60, regenerate with better Stage 1 settings")

        print(f"\n⚠️  IMPORTANT: This script uses PLACEHOLDER Stage 1 generation!")
        print(f"   To use real voice cloning, integrate F5-TTS or StyleTTS2")
        print(f"   See: TWO_STAGE_VOICE_CLONING_GUIDE.md")
        print(f"\n" + "=" * 70 + "\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print(" Two-Stage Voice Cloning Pipeline")
        print("=" * 70)
        print("\nUsage:")
        print("  python generate_two_stage_samples.py <original_sample.wav> [num_samples]")
        print("\nExample:")
        print("  python generate_two_stage_samples.py my_voice.wav 5")
        print("\nArguments:")
        print("  original_sample.wav  - Path to original voice sample")
        print("  num_samples         - Number of samples to generate (default: 5)")
        print("\nOutput:")
        print("  Samples will be saved to: /home/user/AiD/voice_samples/")
        print("=" * 70)
        sys.exit(1)

    # Get arguments
    original_sample = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    # Validate arguments
    if not os.path.exists(original_sample):
        print(f"❌ Error: File not found: {original_sample}")
        sys.exit(1)

    if num_samples < 1 or num_samples > 20:
        print(f"❌ Error: num_samples must be between 1 and 20 (got: {num_samples})")
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
        pipeline = TwoStageVoicePipeline(original_sample)
        pipeline.run_pipeline(num_samples=num_samples)
    except Exception as e:
        print(f"\n❌ Error: Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
