# TTS Compatibility Fix

## Issue
While XTTS v2 loads successfully with the BeamSearchScorer compatibility patch, speech generation fails with:
```
'GPT2InferenceModel' object has no attribute 'generate'
```

## Root Cause
TTS 0.22.0 is incompatible with transformers 4.50+. In transformers 4.50, the generation interface was changed and `GPT2InferenceModel` no longer inherits the `generate` method from `GenerationMixin`.

Additionally, newer versions of `peft` (0.14+) require `transformers.modeling_layers` which was only added in transformers 4.50+.

## Solution
Downgrade both transformers and peft to versions compatible with TTS 0.22.0.

### Steps to Fix:

1. **Uninstall incompatible packages:**
   ```bash
   pip uninstall transformers peft
   ```

2. **Install compatible versions:**
   ```bash
   pip install "transformers>=4.35.0,<4.50.0" "peft>=0.9.0,<0.14.0"
   ```

   Recommended versions:
   - transformers==4.45.2 (latest before the breaking change)
   - peft==0.13.2 (latest compatible with transformers <4.50)

3. **Restart the bot**

## Verified Compatible Versions

### transformers
- ✅ transformers 4.35.x - 4.45.x with TTS 0.22.0
- ✅ transformers 4.45.2 (recommended - latest stable before breaking changes)
- ❌ transformers 4.50.0+ (breaks TTS 0.22.0)
- ❌ transformers 4.57.1 (current installed - too new)

### peft
- ✅ peft 0.9.x - 0.13.x with transformers <4.50
- ✅ peft 0.13.2 (recommended)
- ❌ peft 0.14.0+ (requires transformers 4.50+)

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
peft>=0.9.0,<0.14.0
```

This ensures future installations use compatible versions.

## Verification

After installing the correct transformers version, you should see:
```
[VOICE DEBUG] ✓ BeamSearchScorer compatibility patch verified and working!
[VOICE] TTS initialized with Coqui TTS (voice cloning)
[VOICE] Using 17 reference sample(s)
```

And when speaking, you should NOT see the generate error - instead you'll see successful speech generation.
