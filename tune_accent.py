#!/usr/bin/env python3
"""
Interactive Accent Tuning for AiD TTS

Generates 5 voice samples at a time with different parameter configurations.
You pick your favorite, and it refines around that choice for 3 rounds total.

Usage:
    python tune_accent.py
"""

import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
from voice_config import VoiceConfig


class AccentTuner:
    """Interactive accent parameter tuning system."""

    def __init__(self):
        self.output_dir = Path("accent_samples")
        self.output_dir.mkdir(exist_ok=True)

        # Test text - should showcase accent characteristics
        self.test_texts = [
            "Hello there! I'm AiD, your artificial intelligence assistant. How can I help you today?",
            "Right then, let's get started with this project, shall we? I reckon we can make brilliant progress.",
            "I've analyzed the data thoroughly, and I must say, the results are quite fascinating indeed.",
        ]

        self.current_text_index = 0
        self.voice_handler = None
        self.round_number = 1

    def init_tts(self):
        """Initialize the TTS system."""
        print("\n🎙️  Initializing TTS system...")
        try:
            from voice_handler import VoiceHandler
            self.voice_handler = VoiceHandler()

            if not self.voice_handler.tts_enabled or self.voice_handler.tts_mode != 'coqui':
                print("❌ ERROR: Coqui TTS is not available!")
                print("   This script requires Coqui XTTS v2 for voice cloning.")
                return False

            print(f"✅ TTS initialized with {len(self.voice_handler.reference_audio)} reference samples")
            return True

        except Exception as e:
            print(f"❌ Error initializing TTS: {e}")
            return False

    def get_test_text(self) -> str:
        """Get the next test text."""
        text = self.test_texts[self.current_text_index]
        self.current_text_index = (self.current_text_index + 1) % len(self.test_texts)
        return text

    def generate_initial_configs(self) -> List[Dict]:
        """Generate 5 diverse initial configurations."""
        return [
            {
                "name": "Subtle Accent",
                "description": "Mild accent with high clarity",
                "TEMPERATURE": 0.60,
                "REPETITION_PENALTY": 3.0,
                "LENGTH_PENALTY": 1.0,
                "TOP_K": 50,
                "TOP_P": 0.85,
                "SPEED": 1.0,
            },
            {
                "name": "Moderate Accent",
                "description": "Balanced accent and stability",
                "TEMPERATURE": 0.72,
                "REPETITION_PENALTY": 2.2,
                "LENGTH_PENALTY": 1.1,
                "TOP_K": 70,
                "TOP_P": 0.90,
                "SPEED": 0.95,
            },
            {
                "name": "Strong Accent",
                "description": "Clear accent emphasis (current)",
                "TEMPERATURE": 0.82,
                "REPETITION_PENALTY": 1.8,
                "LENGTH_PENALTY": 1.2,
                "TOP_K": 90,
                "TOP_P": 0.94,
                "SPEED": 0.92,
            },
            {
                "name": "Very Strong Accent",
                "description": "Maximum accent, some variation",
                "TEMPERATURE": 0.88,
                "REPETITION_PENALTY": 1.5,
                "LENGTH_PENALTY": 1.25,
                "TOP_K": 100,
                "TOP_P": 0.96,
                "SPEED": 0.90,
            },
            {
                "name": "Ultra Expressive",
                "description": "Extreme accent emphasis",
                "TEMPERATURE": 0.92,
                "REPETITION_PENALTY": 1.2,
                "LENGTH_PENALTY": 1.3,
                "TOP_K": 110,
                "TOP_P": 0.97,
                "SPEED": 0.88,
            },
        ]

    def generate_refined_configs(self, base_config: Dict) -> List[Dict]:
        """Generate 5 variations around a base configuration."""
        configs = []

        # Extract base values
        base_temp = base_config["TEMPERATURE"]
        base_rep_pen = base_config["REPETITION_PENALTY"]
        base_len_pen = base_config["LENGTH_PENALTY"]
        base_top_k = base_config["TOP_K"]
        base_top_p = base_config["TOP_P"]
        base_speed = base_config["SPEED"]

        # Variation magnitude decreases with each round
        variation = 0.1 if self.round_number == 2 else 0.05

        # Config 1: Exact base (for comparison)
        configs.append({
            "name": f"Base Config",
            "description": "Your previous favorite",
            **{k: v for k, v in base_config.items() if k not in ["name", "description"]}
        })

        # Config 2: Higher temperature (more expressive)
        configs.append({
            "name": "More Expressive",
            "description": "Higher temperature for more variation",
            "TEMPERATURE": min(0.99, base_temp + variation),
            "REPETITION_PENALTY": base_rep_pen,
            "LENGTH_PENALTY": base_len_pen,
            "TOP_K": base_top_k,
            "TOP_P": min(0.99, base_top_p + variation * 0.5),
            "SPEED": base_speed,
        })

        # Config 3: Lower repetition penalty (more natural patterns)
        configs.append({
            "name": "More Natural Flow",
            "description": "Lower penalty for natural accent patterns",
            "TEMPERATURE": base_temp,
            "REPETITION_PENALTY": max(1.0, base_rep_pen - variation * 5),
            "LENGTH_PENALTY": base_len_pen,
            "TOP_K": base_top_k,
            "TOP_P": base_top_p,
            "SPEED": base_speed,
        })

        # Config 4: Higher TOP_K/TOP_P (more diversity)
        configs.append({
            "name": "More Diverse",
            "description": "Higher sampling diversity",
            "TEMPERATURE": base_temp,
            "REPETITION_PENALTY": base_rep_pen,
            "LENGTH_PENALTY": base_len_pen,
            "TOP_K": min(150, int(base_top_k + 20)),
            "TOP_P": min(0.99, base_top_p + variation * 0.3),
            "SPEED": base_speed,
        })

        # Config 5: Slower/more deliberate
        configs.append({
            "name": "More Deliberate",
            "description": "Slower pacing for clearer accent",
            "TEMPERATURE": base_temp,
            "REPETITION_PENALTY": base_rep_pen,
            "LENGTH_PENALTY": base_len_pen + variation,
            "TOP_K": base_top_k,
            "TOP_P": base_top_p,
            "SPEED": max(0.75, base_speed - 0.05),
        })

        return configs

    def apply_config(self, config: Dict):
        """Apply a configuration to VoiceConfig."""
        VoiceConfig.TEMPERATURE = config["TEMPERATURE"]
        VoiceConfig.REPETITION_PENALTY = config["REPETITION_PENALTY"]
        VoiceConfig.LENGTH_PENALTY = config["LENGTH_PENALTY"]
        VoiceConfig.TOP_K = config["TOP_K"]
        VoiceConfig.TOP_P = config["TOP_P"]
        VoiceConfig.SPEED = config["SPEED"]
        VoiceConfig.ENABLE_TEXT_SPLITTING = True

    def generate_sample(self, config: Dict, sample_num: int, text: str) -> Tuple[int, str, bool]:
        """Generate a single audio sample with given config."""
        try:
            # Apply configuration
            self.apply_config(config)

            # Generate filename
            timestamp = int(time.time())
            filename = self.output_dir / f"sample_{sample_num}_round{self.round_number}_{timestamp}.wav"

            # Generate speech
            success = self.voice_handler._speak_coqui(
                text=text,
                output_file=str(filename),
                play_audio=False
            )

            if success:
                return sample_num, str(filename), True
            else:
                return sample_num, "", False

        except Exception as e:
            print(f"❌ Error generating sample {sample_num}: {e}")
            return sample_num, "", False

    def generate_samples_parallel(self, configs: List[Dict], text: str) -> Dict[int, str]:
        """Generate multiple samples in parallel."""
        print(f"\n🎵 Generating 5 samples in parallel...")
        print(f"📝 Text: \"{text}\"\n")

        results = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.generate_sample, config, i+1, text): (i+1, config)
                for i, config in enumerate(configs)
            }

            # Collect results as they complete
            for future in as_completed(futures):
                sample_num, filename, success = future.result()
                if success:
                    results[sample_num] = filename
                    print(f"  ✅ Sample {sample_num} complete")
                else:
                    print(f"  ❌ Sample {sample_num} failed")

        return results

    def display_configs(self, configs: List[Dict]):
        """Display configuration parameters in a readable format."""
        print("\n" + "="*80)
        print(f"ROUND {self.round_number} - SAMPLE CONFIGURATIONS")
        print("="*80)

        for i, config in enumerate(configs, 1):
            print(f"\n【 SAMPLE {i} - {config['name']} 】")
            print(f"   {config['description']}")
            print(f"   ┌─────────────────────────────────────────┐")
            print(f"   │ Temperature:       {config['TEMPERATURE']:.2f}              │")
            print(f"   │ Repetition Penalty: {config['REPETITION_PENALTY']:.1f}             │")
            print(f"   │ Length Penalty:     {config['LENGTH_PENALTY']:.2f}             │")
            print(f"   │ Top-K:             {config['TOP_K']:>3}              │")
            print(f"   │ Top-P:              {config['TOP_P']:.2f}             │")
            print(f"   │ Speed:              {config['SPEED']:.2f}             │")
            print(f"   └─────────────────────────────────────────┘")

        print("\n" + "="*80)

    def get_user_choice(self, num_samples: int) -> int:
        """Get user's favorite sample."""
        while True:
            try:
                choice = input(f"\n🎯 Which sample has the BEST accent? (1-{num_samples}, or 'q' to quit): ").strip()

                if choice.lower() == 'q':
                    return -1

                choice = int(choice)
                if 1 <= choice <= num_samples:
                    return choice
                else:
                    print(f"❌ Please enter a number between 1 and {num_samples}")

            except ValueError:
                print("❌ Please enter a valid number")

    def save_final_config(self, config: Dict):
        """Save the final configuration to a Python file."""
        output_file = self.output_dir / "best_config.py"

        with open(output_file, 'w') as f:
            f.write("# Best Accent Configuration\n")
            f.write("# Generated by tune_accent.py\n\n")
            f.write("# Apply this to voice_config.py by copying these values:\n\n")
            f.write(f'TEMPERATURE = {config["TEMPERATURE"]}\n')
            f.write(f'REPETITION_PENALTY = {config["REPETITION_PENALTY"]}\n')
            f.write(f'LENGTH_PENALTY = {config["LENGTH_PENALTY"]}\n')
            f.write(f'TOP_K = {config["TOP_K"]}\n')
            f.write(f'TOP_P = {config["TOP_P"]}\n')
            f.write(f'SPEED = {config["SPEED"]}\n')
            f.write('ENABLE_TEXT_SPLITTING = True\n')

        print(f"\n💾 Best configuration saved to: {output_file}")

    def apply_to_voice_config(self, config: Dict):
        """Apply the selected config to voice_config.py."""
        print("\n" + "="*80)
        print("FINAL CONFIGURATION")
        print("="*80)
        print(f"\n{config['name']} - {config['description']}")
        print(f"\nTEMPERATURE = {config['TEMPERATURE']}")
        print(f"REPETITION_PENALTY = {config['REPETITION_PENALTY']}")
        print(f"LENGTH_PENALTY = {config['LENGTH_PENALTY']}")
        print(f"TOP_K = {config['TOP_K']}")
        print(f"TOP_P = {config['TOP_P']}")
        print(f"SPEED = {config['SPEED']}")
        print("\n" + "="*80)

        response = input("\n📝 Apply this configuration to voice_config.py? (y/n): ").strip().lower()

        if response == 'y':
            try:
                # Read current file
                config_file = Path(__file__).parent / "voice_config.py"
                with open(config_file, 'r') as f:
                    lines = f.readlines()

                # Update parameter values
                new_lines = []
                for line in lines:
                    if line.strip().startswith("TEMPERATURE ="):
                        new_lines.append(f"    TEMPERATURE = {config['TEMPERATURE']}\n")
                    elif line.strip().startswith("REPETITION_PENALTY ="):
                        new_lines.append(f"    REPETITION_PENALTY = {config['REPETITION_PENALTY']}\n")
                    elif line.strip().startswith("LENGTH_PENALTY ="):
                        new_lines.append(f"    LENGTH_PENALTY = {config['LENGTH_PENALTY']}\n")
                    elif line.strip().startswith("TOP_K ="):
                        new_lines.append(f"    TOP_K = {config['TOP_K']}\n")
                    elif line.strip().startswith("TOP_P ="):
                        new_lines.append(f"    TOP_P = {config['TOP_P']}\n")
                    elif line.strip().startswith("SPEED =") and "ACCENT EMPHASIS" in "".join(lines[max(0, len(new_lines)-5):len(new_lines)]):
                        new_lines.append(f"    SPEED = {config['SPEED']}\n")
                    else:
                        new_lines.append(line)

                # Write back
                with open(config_file, 'w') as f:
                    f.writelines(new_lines)

                print("✅ Configuration applied to voice_config.py!")

            except Exception as e:
                print(f"❌ Error applying configuration: {e}")
                print("   You can manually copy the values from accent_samples/best_config.py")

    def run(self):
        """Run the interactive tuning process."""
        print("\n" + "="*80)
        print("🎙️  AiD ACCENT TUNER - Interactive Parameter Optimization")
        print("="*80)
        print("\nThis tool will help you find the perfect accent parameters.")
        print("You'll hear 5 samples at a time, pick your favorite, and we'll")
        print("refine the parameters over 3 rounds to find the ideal settings.")
        print("\n" + "="*80)

        # Initialize TTS
        if not self.init_tts():
            return

        print("\n📁 Audio samples will be saved to:", self.output_dir.absolute())

        input("\n▶️  Press ENTER to start Round 1...")

        # Round 1: Initial diverse configs
        configs = self.generate_initial_configs()
        text = self.get_test_text()

        self.display_configs(configs)
        results = self.generate_samples_parallel(configs, text)

        if len(results) < 5:
            print("\n❌ Failed to generate all samples. Please check TTS configuration.")
            return

        print(f"\n✅ All samples generated! Check the '{self.output_dir}' folder.")
        print("   Listen to each sample and note which has the best accent.")

        choice = self.get_user_choice(5)
        if choice == -1:
            print("\n👋 Tuning cancelled.")
            return

        selected_config = configs[choice - 1]
        print(f"\n✅ Selected: Sample {choice} - {selected_config['name']}")

        # Round 2: Refine around selection
        self.round_number = 2
        input(f"\n▶️  Press ENTER to start Round 2 (refining around '{selected_config['name']}')...")

        configs = self.generate_refined_configs(selected_config)
        text = self.get_test_text()

        self.display_configs(configs)
        results = self.generate_samples_parallel(configs, text)

        print(f"\n✅ Round 2 samples generated! Check the '{self.output_dir}' folder.")

        choice = self.get_user_choice(5)
        if choice == -1:
            print("\n👋 Tuning cancelled.")
            return

        selected_config = configs[choice - 1]
        print(f"\n✅ Selected: Sample {choice} - {selected_config['name']}")

        # Round 3: Final refinement
        self.round_number = 3
        input(f"\n▶️  Press ENTER to start Round 3 (final refinement)...")

        configs = self.generate_refined_configs(selected_config)
        text = self.get_test_text()

        self.display_configs(configs)
        results = self.generate_samples_parallel(configs, text)

        print(f"\n✅ Round 3 samples generated! Check the '{self.output_dir}' folder.")

        choice = self.get_user_choice(5)
        if choice == -1:
            print("\n👋 Tuning cancelled.")
            return

        final_config = configs[choice - 1]
        print(f"\n🎉 Final selection: Sample {choice} - {final_config['name']}")

        # Save and optionally apply
        self.save_final_config(final_config)
        self.apply_to_voice_config(final_config)

        print("\n" + "="*80)
        print("✅ ACCENT TUNING COMPLETE!")
        print("="*80)
        print(f"\n📁 All samples saved in: {self.output_dir.absolute()}")
        print("🎵 You can re-listen to any sample to compare")
        print("\n👋 Happy voicing!")


if __name__ == "__main__":
    tuner = AccentTuner()
    try:
        tuner.run()
    except KeyboardInterrupt:
        print("\n\n👋 Tuning interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
