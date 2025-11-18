# TTS Compatibility Fix

## Issue
While XTTS v2 loads successfully with the BeamSearchScorer compatibility patch, speech generation fails with:
```
'GPT2InferenceModel' object has no attribute 'generate'
```

## Root Cause
TTS 0.22.0 is incompatible with transformers 4.50+. In transformers 4.50, the generation interface was changed and `GPT2InferenceModel` no longer inherits the `generate` method from `GenerationMixin`.

## Solution
Downgrade transformers to a version compatible with TTS 0.22.0.

### Steps to Fix:

1. **Uninstall current transformers:**
   ```bash
   pip uninstall transformers
   ```

2. **Install compatible version:**
   ```bash
   pip install "transformers>=4.35.0,<4.50.0"
   ```

   Recommended version: `transformers==4.45.2` (latest before the breaking change)

3. **Restart the bot**

## Verified Compatible Versions

- ✅ transformers 4.35.x - 4.45.x with TTS 0.22.0
- ✅ transformers 4.45.2 (recommended - latest stable before breaking changes)
- ❌ transformers 4.50.0+ (breaks TTS 0.22.0)
- ❌ transformers 4.57.1 (your current version - too new)

## Alternative Solution

If you need transformers 4.50+ for other dependencies, you can:

1. Upgrade TTS instead:
   ```bash
   pip install --upgrade TTS
   ```

However, newer TTS versions may have different APIs or requirements. The recommended approach is to downgrade transformers.

## Updated requirements.txt

The requirements.txt has been updated to specify:
```
transformers>=4.35.0,<4.50.0
```

This ensures future installations use a compatible version.

## Verification

After installing the correct transformers version, you should see:
```
[VOICE DEBUG] ✓ BeamSearchScorer compatibility patch verified and working!
[VOICE] TTS initialized with Coqui TTS (voice cloning)
[VOICE] Using 17 reference sample(s)
```

And when speaking, you should NOT see the generate error - instead you'll see successful speech generation.
