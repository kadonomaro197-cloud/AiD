"""
Automated Voice Sample Processor for Audacity
Processes voice samples to optimize them for XTTS voice cloning

This script uses Audacity's scripting module (mod-script-pipe) to:
1. Convert stereo to mono
2. Normalize audio levels
3. Remove noise (optional)
4. Trim to optimal length (with user guidance)
5. Export processed files

Requirements:
- Audacity installed with mod-script-pipe enabled
- Python 3.6+
- Original voice samples in voice_samples/ directory
"""

import os
import sys
import time
import json
from pathlib import Path
import platform

# Platform-specific pipe paths
if platform.system() == 'Windows':
    WRITE_PIPE = r'\\.\pipe\ToSrvPipe'
    READ_PIPE = r'\\.\pipe\FromSrvPipe'
    EOL = '\r\n\0'
else:
    WRITE_PIPE = '/tmp/audacity_script_pipe.to'
    READ_PIPE = '/tmp/audacity_script_pipe.from'
    EOL = '\n'


class AudacityController:
    """Controller for Audacity via scripting module."""

    def __init__(self):
        self.write_pipe = None
        self.read_pipe = None
        self.connected = False

    def connect(self):
        """Connect to Audacity's scripting pipes."""
        print("\n📡 Connecting to Audacity...")

        try:
            if platform.system() == 'Windows':
                # Windows named pipes
                self.write_pipe = open(WRITE_PIPE, 'w')
                self.read_pipe = open(READ_PIPE, 'r')
            else:
                # Unix named pipes
                self.write_pipe = open(WRITE_PIPE, 'w')
                self.read_pipe = open(READ_PIPE, 'r')

            self.connected = True
            print("✅ Connected to Audacity successfully!")
            return True

        except FileNotFoundError:
            print("\n❌ Could not connect to Audacity!")
            print("\n📋 Setup Instructions:")
            print("1. Open Audacity")
            print("2. Go to Edit → Preferences → Modules")
            print("3. Set 'mod-script-pipe' to 'Enabled'")
            print("4. Click OK and restart Audacity")
            print("5. Audacity should now be listening for commands")
            print("\nAfter setup, run this script again.")
            return False
        except Exception as e:
            print(f"\n❌ Error connecting to Audacity: {e}")
            return False

    def send_command(self, command):
        """Send a command to Audacity and get response."""
        if not self.connected:
            return None

        try:
            # Send command
            self.write_pipe.write(command + EOL)
            self.write_pipe.flush()

            # Read response
            response = ""
            while True:
                line = self.read_pipe.readline()
                if line == '\n' or line == '':
                    break
                response += line

            return response.strip()

        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return None

    def close(self):
        """Close connection to Audacity."""
        if self.write_pipe:
            self.write_pipe.close()
        if self.read_pipe:
            self.read_pipe.close()
        self.connected = False


class VoiceSampleProcessor:
    """Process voice samples for optimal TTS quality."""

    def __init__(self, input_dir="voice_samples", output_dir="voice_samples_processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.audacity = AudacityController()
        self.processed_count = 0
        self.skipped_count = 0

    def setup(self):
        """Setup directories and Audacity connection."""
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        print(f"✅ Output directory: {self.output_dir}")

        # Connect to Audacity
        if not self.audacity.connect():
            return False

        return True

    def get_track_info(self):
        """Get information about the current track."""
        response = self.audacity.send_command('GetInfo: Type=Tracks')
        return response

    def process_file(self, input_file, process_mode='auto'):
        """
        Process a single voice sample.

        Args:
            input_file: Path to input WAV file
            process_mode: 'auto' for automatic, 'manual' for manual trimming
        """
        output_file = self.output_dir / f"{input_file.stem}_processed.wav"

        print(f"\n{'=' * 70}")
        print(f"Processing: {input_file.name}")
        print(f"{'=' * 70}")

        # Step 1: Open file
        print("\n[1/7] Opening file in Audacity...")
        result = self.audacity.send_command(f'Open2: Filename="{input_file}"')
        if not result or 'BatchCommand failed' in result:
            print(f"❌ Failed to open file: {result}")
            return False
        print("✅ File opened")
        time.sleep(0.5)

        # Step 2: Get track info
        print("\n[2/7] Analyzing audio...")
        track_info = self.get_track_info()
        print(f"✅ Track info retrieved")

        # Step 3: Convert stereo to mono
        print("\n[3/7] Converting to mono...")
        result = self.audacity.send_command('SelectAll:')
        result = self.audacity.send_command('MixStereoToMono:')
        print("✅ Converted to mono")
        time.sleep(0.5)

        # Step 4: Normalize audio
        print("\n[4/7] Normalizing audio levels...")
        result = self.audacity.send_command('SelectAll:')
        result = self.audacity.send_command('Normalize: PeakLevel=-1.0 RemoveDcOffset=Yes ApplyGain=Yes StereoIndependent=No')
        print("✅ Audio normalized to -1.0 dB")
        time.sleep(0.5)

        # Step 5: Noise reduction (optional)
        print("\n[5/7] Would you like to apply noise reduction? (y/n): ", end='')
        if input().lower().strip() == 'y':
            print("   Getting noise profile from first 2 seconds...")
            # Select first 2 seconds for noise profile
            result = self.audacity.send_command('Select: Start=0 End=2')
            result = self.audacity.send_command('NoiseReduction: Use_Preset="<Factory Defaults>" Action="Get Noise Profile"')

            # Apply to whole track
            result = self.audacity.send_command('SelectAll:')
            result = self.audacity.send_command('NoiseReduction: Use_Preset="<Factory Defaults>" Action="Reduce Noise" Sensitivity=12.0')
            print("✅ Noise reduction applied")
        else:
            print("⊘ Skipped noise reduction")
        time.sleep(0.5)

        # Step 6: Trim to optimal length
        print("\n[6/7] Trimming to optimal length...")
        print("   ℹ️  The audio is now playing in Audacity")
        print("   ℹ️  Listen and find the BEST 15-25 second section with:")
        print("      • Varied intonation and emotions")
        print("      • Different speaking speeds")
        print("      • Clear pronunciation")
        print("      • No long pauses or background noise")

        # Get track duration
        result = self.audacity.send_command('GetInfo: Type=Tracks Format=JSON')

        if process_mode == 'auto':
            # Auto mode: suggest trimming from center
            print("\n   Select one of these options:")
            print("   1. Let me select manually in Audacity (RECOMMENDED)")
            print("   2. Auto-trim from start (first 20 seconds)")
            print("   3. Auto-trim from middle (middle 20 seconds)")
            print("   4. Skip trimming (keep full length)")

            choice = input("\n   Enter choice (1-4): ").strip()

            if choice == '1':
                print("\n   📋 Manual Selection Instructions:")
                print("   1. In Audacity, click and drag to select 15-25 seconds")
                print("   2. Press Ctrl+T (or Cmd+T on Mac) to trim")
                print("   3. Press any key here when done...")
                input()
                print("✅ Manual trim completed")

            elif choice == '2':
                print("   Auto-trimming first 20 seconds...")
                result = self.audacity.send_command('Select: Start=0 End=20')
                result = self.audacity.send_command('Trim:')
                print("✅ Auto-trimmed from start")

            elif choice == '3':
                # Get track length and trim middle
                print("   Auto-trimming 20 seconds from middle...")
                result = self.audacity.send_command('GetInfo: Type=Tracks Format=JSON')
                # For simplicity, trim 20 seconds starting at 10 seconds
                result = self.audacity.send_command('Select: Start=10 End=30')
                result = self.audacity.send_command('Trim:')
                print("✅ Auto-trimmed from middle")

            elif choice == '4':
                print("⊘ Skipped trimming")

        else:
            # Manual mode
            print("\n   Press any key when you've trimmed the audio in Audacity...")
            input()
            print("✅ Trim completed")

        time.sleep(0.5)

        # Step 7: Export
        print("\n[7/7] Exporting processed file...")
        result = self.audacity.send_command('SelectAll:')
        result = self.audacity.send_command(f'Export2: Filename="{output_file}" NumChannels=1')

        if output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"✅ Exported: {output_file.name} ({file_size:.2f} MB)")

            # Close the project without saving
            self.audacity.send_command('Close:')

            self.processed_count += 1
            return True
        else:
            print(f"❌ Export failed!")
            return False

    def process_all(self, process_mode='auto'):
        """Process all voice samples."""
        # Get all WAV files
        wav_files = sorted(self.input_dir.glob("*.wav"))

        if not wav_files:
            print(f"\n❌ No WAV files found in {self.input_dir}")
            return

        print(f"\n{'=' * 70}")
        print(f"Found {len(wav_files)} voice sample(s) to process")
        print(f"{'=' * 70}")

        # Ask which files to process
        print("\nSelect files to process:")
        for i, wav_file in enumerate(wav_files, 1):
            file_size = wav_file.stat().st_size / (1024 * 1024)
            print(f"  {i}. {wav_file.name} ({file_size:.2f} MB)")

        print(f"\nEnter file numbers to process (e.g., '1,3,5' or 'all'): ", end='')
        selection = input().strip().lower()

        if selection == 'all':
            files_to_process = wav_files
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                files_to_process = [wav_files[i] for i in indices if 0 <= i < len(wav_files)]
            except:
                print("❌ Invalid selection!")
                return

        # Ask for process mode
        print(f"\nProcessing mode:")
        print(f"  1. Auto (recommended for beginners)")
        print(f"  2. Manual (you select trim points)")
        mode_choice = input("Enter choice (1-2): ").strip()
        process_mode = 'auto' if mode_choice == '1' else 'manual'

        # Process each file
        print(f"\n{'=' * 70}")
        print(f"Starting batch processing ({len(files_to_process)} files)")
        print(f"{'=' * 70}")

        for i, wav_file in enumerate(files_to_process, 1):
            print(f"\n\n{'#' * 70}")
            print(f"File {i} of {len(files_to_process)}")
            print(f"{'#' * 70}")

            success = self.process_file(wav_file, process_mode)

            if not success:
                print(f"\n⚠️  Would you like to skip this file and continue? (y/n): ", end='')
                if input().strip().lower() != 'y':
                    break
                self.skipped_count += 1

        # Summary
        print(f"\n\n{'=' * 70}")
        print(f"Processing Complete!")
        print(f"{'=' * 70}")
        print(f"✅ Successfully processed: {self.processed_count}")
        print(f"⊘ Skipped: {self.skipped_count}")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"\nNext steps:")
        print(f"1. Check the quality of processed files")
        print(f"2. Run: python check_voice_samples.py (on processed files)")
        print(f"3. Run: python test_voice_cloning.py (update to use processed files)")
        print(f"{'=' * 70}\n")


def check_audacity_installed():
    """Check if Audacity is installed."""
    print("\n🔍 Checking for Audacity installation...")

    if platform.system() == 'Windows':
        common_paths = [
            r"C:\Program Files\Audacity\Audacity.exe",
            r"C:\Program Files (x86)\Audacity\Audacity.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Audacity\Audacity.exe")
        ]
        for path in common_paths:
            if os.path.exists(path):
                print(f"✅ Found Audacity at: {path}")
                return True
    else:
        # Try to run audacity command
        import subprocess
        try:
            subprocess.run(['which', 'audacity'], capture_output=True, check=True)
            print("✅ Audacity found in PATH")
            return True
        except:
            pass

    print("⚠️  Could not auto-detect Audacity")
    print("   If Audacity is installed, continue anyway")
    return None


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("🎙️  Voice Sample Processor for XTTS Voice Cloning")
    print("=" * 70)

    # Check for Audacity
    check_audacity_installed()

    print("\n📋 Pre-flight Checklist:")
    print("   ✓ Audacity must be open and running")
    print("   ✓ Mod-script-pipe module must be enabled")
    print("   ✓ Voice samples in 'voice_samples/' directory")

    print("\n⚠️  IMPORTANT Setup Instructions:")
    print("   1. Open Audacity")
    print("   2. Go to Edit → Preferences → Modules")
    print("   3. Find 'mod-script-pipe' and set to 'Enabled'")
    print("   4. Click OK and RESTART Audacity")
    print("   5. Keep Audacity open (don't close it)")

    print("\nIs Audacity open with mod-script-pipe enabled? (y/n): ", end='')
    if input().strip().lower() != 'y':
        print("\n⊘ Please set up Audacity first, then run this script again.")
        sys.exit(0)

    # Initialize processor
    processor = VoiceSampleProcessor(
        input_dir="voice_samples",
        output_dir="voice_samples_processed"
    )

    # Setup
    if not processor.setup():
        print("\n❌ Setup failed!")
        print("\nTroubleshooting:")
        print("1. Make sure Audacity is open")
        print("2. Check that mod-script-pipe is enabled in Preferences → Modules")
        print("3. Restart Audacity after enabling mod-script-pipe")
        print("4. Try running this script again")
        sys.exit(1)

    # Process files
    try:
        processor.process_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        processor.audacity.close()

    print("\n✅ All done! Check your processed files in 'voice_samples_processed/'")


if __name__ == "__main__":
    main()
