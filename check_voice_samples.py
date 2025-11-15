"""
Voice Sample Quality Checker
Analyzes voice samples for optimal XTTS voice cloning
"""

import os
from pathlib import Path
import wave
import numpy as np


def analyze_audio_quality(file_path):
    """Analyze a WAV file for voice cloning suitability."""
    try:
        with wave.open(str(file_path), 'rb') as wav_file:
            # Get basic properties
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            duration = n_frames / float(framerate)

            # Read audio data
            audio_data = wav_file.readframes(n_frames)

            # Convert to numpy array
            if sample_width == 2:  # 16-bit
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            elif sample_width == 4:  # 32-bit
                audio_array = np.frombuffer(audio_data, dtype=np.int32)
            else:
                audio_array = None

            # Calculate metrics
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            # Quality assessment
            issues = []
            recommendations = []

            # Check duration
            if duration < 6:
                issues.append(f"Duration too short: {duration:.1f}s (optimal: 6-30s)")
                recommendations.append("Use longer clips with varied speech")
            elif duration > 30:
                issues.append(f"Duration too long: {duration:.1f}s (optimal: 6-30s)")
                recommendations.append("Trim to 15-25 seconds of varied speech")

            # Check sample rate
            if framerate < 22050:
                issues.append(f"Low sample rate: {framerate}Hz")
                recommendations.append("Use 22050Hz or 44100Hz sample rate")
            elif framerate > 48000:
                issues.append(f"Very high sample rate: {framerate}Hz (may be unnecessary)")

            # Check channels
            if channels > 1:
                issues.append(f"Stereo audio detected ({channels} channels)")
                recommendations.append("Convert to mono for better results")

            # Check for silence (if we have audio data)
            if audio_array is not None:
                # Calculate RMS (volume level)
                rms = np.sqrt(np.mean(audio_array.astype(float)**2))
                max_val = np.max(np.abs(audio_array))

                # Normalize to 0-1 range
                if sample_width == 2:
                    max_possible = 32768
                else:
                    max_possible = 2147483648

                normalized_rms = rms / max_possible
                normalized_max = max_val / max_possible

                # Check for low volume
                if normalized_rms < 0.05:
                    issues.append(f"Very quiet audio (RMS: {normalized_rms:.4f})")
                    recommendations.append("Increase recording volume or normalize audio")

                # Check for clipping
                if normalized_max > 0.95:
                    issues.append("Audio may be clipping (too loud)")
                    recommendations.append("Reduce volume to avoid distortion")

            return {
                'file_size_mb': file_size_mb,
                'duration': duration,
                'sample_rate': framerate,
                'channels': channels,
                'bit_depth': sample_width * 8,
                'issues': issues,
                'recommendations': recommendations,
                'quality_score': calculate_quality_score(duration, framerate, channels, issues)
            }

    except Exception as e:
        return {
            'error': str(e)
        }


def calculate_quality_score(duration, sample_rate, channels, issues):
    """Calculate a quality score from 0-100."""
    score = 100

    # Deduct points for issues
    score -= len(issues) * 15

    # Duration score
    if 10 <= duration <= 20:
        score += 0  # Perfect
    elif 6 <= duration <= 30:
        score -= 5  # Good
    else:
        score -= 20  # Poor

    # Sample rate score
    if sample_rate in [22050, 44100]:
        score += 0  # Perfect
    else:
        score -= 10

    # Channels
    if channels == 1:
        score += 0  # Perfect
    else:
        score -= 10

    return max(0, min(100, score))


def main():
    print("\n" + "=" * 70)
    print("Voice Sample Quality Analyzer")
    print("=" * 70)

    voice_samples_dir = Path("voice_samples")

    if not voice_samples_dir.exists():
        print(f"\n❌ Directory not found: {voice_samples_dir}")
        return

    voice_files = list(voice_samples_dir.glob("*.wav"))

    if not voice_files:
        print(f"\n❌ No WAV files found in {voice_samples_dir}")
        return

    print(f"\nAnalyzing {len(voice_files)} voice sample(s)...\n")

    all_recommendations = set()

    for i, voice_file in enumerate(voice_files, 1):
        print(f"\n{'─' * 70}")
        print(f"[{i}/{len(voice_files)}] {voice_file.name}")
        print(f"{'─' * 70}")

        analysis = analyze_audio_quality(voice_file)

        if 'error' in analysis:
            print(f"❌ Error analyzing file: {analysis['error']}")
            continue

        # Display properties
        print(f"\n📊 Properties:")
        print(f"   File size:    {analysis['file_size_mb']:.2f} MB")
        print(f"   Duration:     {analysis['duration']:.2f} seconds")
        print(f"   Sample rate:  {analysis['sample_rate']} Hz")
        print(f"   Channels:     {analysis['channels']} ({'Mono' if analysis['channels'] == 1 else 'Stereo'})")
        print(f"   Bit depth:    {analysis['bit_depth']} bit")

        # Quality score
        score = analysis['quality_score']
        if score >= 80:
            emoji = "✅"
            rating = "Excellent"
        elif score >= 60:
            emoji = "✓"
            rating = "Good"
        elif score >= 40:
            emoji = "⚠️"
            rating = "Fair"
        else:
            emoji = "❌"
            rating = "Poor"

        print(f"\n{emoji} Quality Score: {score}/100 ({rating})")

        # Issues
        if analysis['issues']:
            print(f"\n⚠️  Issues Found:")
            for issue in analysis['issues']:
                print(f"   • {issue}")
        else:
            print(f"\n✅ No issues detected!")

        # Recommendations
        if analysis['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   • {rec}")
                all_recommendations.add(rec)

    # Summary
    print(f"\n{'=' * 70}")
    print("Summary")
    print(f"{'=' * 70}")

    if all_recommendations:
        print(f"\n📝 Overall Recommendations:")
        for rec in sorted(all_recommendations):
            print(f"   • {rec}")
    else:
        print(f"\n✅ All samples look good for voice cloning!")

    print(f"\n💡 Tips for best results:")
    print(f"   • Use clean recordings without background noise")
    print(f"   • Include varied intonation and emotions")
    print(f"   • Ensure consistent audio quality across samples")
    print(f"   • Trim silence from start/end of clips")
    print(f"   • Use samples from the same speaker/character")

    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    main()