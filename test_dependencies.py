#!/usr/bin/env python3
"""
Test script to verify that the transformers, accelerate, huggingface_hub,
and coqui-tts dependencies are correctly installed and compatible.

This script tests the specific imports that were failing:
- split_torch_state_dict_into_shards from huggingface_hub
- transformers.generation.utils
- transformers.models.gpt2.modeling_gpt2
- transformers.models.bert.modeling_bert
- BeamSearchScorer from transformers (for TTS compatibility)
- TTS library initialization
"""

import sys
import warnings
warnings.filterwarnings('ignore')  # Suppress TTS warnings during import tests

def test_huggingface_hub():
    """Test that huggingface_hub has the required function."""
    print("Testing huggingface_hub...")
    try:
        from huggingface_hub import split_torch_state_dict_into_shards
        print("✓ Successfully imported split_torch_state_dict_into_shards from huggingface_hub")
        return True
    except ImportError as e:
        print(f"✗ Failed to import from huggingface_hub: {e}")
        return False

def test_accelerate():
    """Test that accelerate can be imported."""
    print("\nTesting accelerate...")
    try:
        from accelerate.hooks import AlignDevicesHook, add_hook_to_module
        print("✓ Successfully imported from accelerate.hooks")
        return True
    except ImportError as e:
        print(f"✗ Failed to import from accelerate: {e}")
        return False

def test_transformers_generation():
    """Test that transformers.generation.utils can be imported."""
    print("\nTesting transformers.generation.utils...")
    try:
        from transformers.generation import GenerationConfig, GenerationMixin
        print("✓ Successfully imported from transformers.generation")
        return True
    except ImportError as e:
        print(f"✗ Failed to import from transformers.generation: {e}")
        return False

def test_transformers_gpt2():
    """Test that GPT2 models can be imported."""
    print("\nTesting transformers.models.gpt2...")
    try:
        from transformers import GPT2PreTrainedModel
        print("✓ Successfully imported GPT2PreTrainedModel from transformers")
        return True
    except ImportError as e:
        print(f"✗ Failed to import GPT2 from transformers: {e}")
        return False

def test_transformers_bert():
    """Test that BERT models can be imported."""
    print("\nTesting transformers.models.bert...")
    try:
        from transformers import BertModel
        print("✓ Successfully imported BertModel from transformers")
        return True
    except ImportError as e:
        print(f"✗ Failed to import BERT from transformers: {e}")
        return False

def test_transformers_beam_search():
    """Test that BeamSearchScorer can be imported (required by TTS)."""
    print("\nTesting transformers BeamSearchScorer...")
    try:
        from transformers import BeamSearchScorer
        print("✓ Successfully imported BeamSearchScorer from transformers")
        return True
    except ImportError as e:
        print(f"✗ Failed to import BeamSearchScorer from transformers: {e}")
        print("  Note: This import is required by Coqui TTS for XTTS models")
        return False

def test_tts_import():
    """Test that TTS library can be imported."""
    print("\nTesting TTS (Coqui TTS) import...")
    try:
        from TTS.api import TTS
        print("✓ Successfully imported TTS from coqui-tts package")
        return True
    except ImportError as e:
        print(f"✗ Failed to import TTS: {e}")
        print("  Make sure you have 'coqui-tts' installed (not the old 'TTS' package)")
        return False

def check_versions():
    """Print installed versions of relevant packages."""
    print("\n" + "="*60)
    print("INSTALLED PACKAGE VERSIONS")
    print("="*60)

    packages = ['huggingface_hub', 'accelerate', 'transformers', 'torch']
    for package in packages:
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"{package:20s}: {version}")
        except ImportError:
            print(f"{package:20s}: NOT INSTALLED")

    # Check TTS separately as it imports as TTS but installs as coqui-tts
    try:
        import TTS
        version = getattr(TTS, '__version__', 'unknown')
        print(f"{'TTS (coqui-tts)':20s}: {version}")
    except ImportError:
        print(f"{'TTS (coqui-tts)':20s}: NOT INSTALLED")

    print("="*60 + "\n")

def main():
    """Run all tests."""
    print("="*60)
    print("DEPENDENCY COMPATIBILITY TEST")
    print("="*60)

    check_versions()

    tests = [
        test_huggingface_hub,
        test_accelerate,
        test_transformers_generation,
        test_transformers_gpt2,
        test_transformers_bert,
        test_transformers_beam_search,
        test_tts_import,
    ]

    results = [test() for test in tests]

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("✓ All dependency tests passed!")
        print("\nThe following should now work:")
        print("  - TTS (Coqui XTTS v2) voice synthesis")
        print("  - RAG system with BERT embeddings")
        print("  - Transformers-based language models")
        print("  - BeamSearchScorer and generation utilities")
        return 0
    else:
        print("✗ Some dependency tests failed.")
        print("\nTo fix, run:")
        print("  pip install -r requirements.txt --upgrade")
        print("\nNote: Make sure to uninstall old 'TTS' package first:")
        print("  pip uninstall TTS")
        print("  pip install coqui-tts")
        return 1

if __name__ == "__main__":
    sys.exit(main())
