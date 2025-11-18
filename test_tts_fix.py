#!/usr/bin/env python3
"""
Test script to verify the TTS import fix for BeamSearchScorer compatibility.
"""

print("=" * 60)
print("Testing TTS Import Fix")
print("=" * 60)

# Test 1: Check if transformers module loads
print("\n[TEST 1] Checking transformers module...")
try:
    import transformers
    print(f"✓ transformers version: {transformers.__version__}")
except ImportError as e:
    print(f"✗ Failed to import transformers: {e}")
    exit(1)

# Test 2: Check if BeamSearchScorer is available
print("\n[TEST 2] Checking BeamSearchScorer availability...")
if hasattr(transformers, 'BeamSearchScorer'):
    print("✓ BeamSearchScorer is already in transformers namespace")
else:
    print("✗ BeamSearchScorer not in transformers namespace (will need patch)")

# Test 3: Try to import BeamSearchScorer from generation module
print("\n[TEST 3] Checking BeamSearchScorer in transformers.generation...")
try:
    from transformers.generation import BeamSearchScorer
    print(f"✓ BeamSearchScorer available in transformers.generation")
except ImportError as e:
    print(f"✗ Failed to import BeamSearchScorer from generation: {e}")

# Test 4: Import voice_handler (which applies the patch)
print("\n[TEST 4] Importing voice_handler (applies compatibility patch)...")
try:
    import voice_handler
    print("✓ voice_handler imported successfully")
except Exception as e:
    print(f"✗ Failed to import voice_handler: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Verify patch was applied
print("\n[TEST 5] Verifying BeamSearchScorer is now accessible...")
if hasattr(transformers, 'BeamSearchScorer'):
    print("✓ BeamSearchScorer is now available in transformers namespace")
else:
    print("✗ Patch was not applied successfully")

# Test 6: Try to import TTS
print("\n[TEST 6] Attempting to import TTS.api...")
try:
    from TTS.api import TTS
    print("✓ TTS.api imported successfully!")
    print("\n" + "=" * 60)
    print("SUCCESS: All tests passed!")
    print("The TTS import fix is working correctly.")
    print("=" * 60)
except ImportError as e:
    print(f"✗ Failed to import TTS.api: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("PARTIAL SUCCESS: Patch applied but TTS import still failed.")
    print("This may be due to other compatibility issues.")
    print("=" * 60)
    exit(1)
except Exception as e:
    print(f"✗ Error importing TTS.api: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
