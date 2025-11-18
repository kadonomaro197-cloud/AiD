# Dependency Fix: Transformers & TTS Import Errors

## Issues

The AID Discord Bot was failing to load critical components due to multiple dependency incompatibilities:

### Issue 1: huggingface_hub ImportError

```
ImportError: cannot import name 'split_torch_state_dict_into_shards' from 'huggingface_hub'
```

This error prevented:
- **RAG System**: BERT-based semantic search from initializing
- **Transformers**: Generation utilities from loading properly

### Issue 2: TTS BeamSearchScorer ImportError

```
ImportError: cannot import name 'BeamSearchScorer' from 'transformers'
```

This error prevented:
- **TTS (Text-to-Speech)**: Coqui XTTS v2 voice synthesis from loading
- **Voice Handler**: Discord voice features from initializing properly

## Root Causes

### Cause 1: Missing huggingface_hub Version Pin

The `transformers` library (version 4.35.0+) depends on `accelerate`, which in turn requires `huggingface_hub>=0.17.0`. The function `split_torch_state_dict_into_shards` was introduced in `huggingface_hub` version 0.17.0.

The original `requirements.txt` did not explicitly pin versions for these transitive dependencies, allowing incompatible older versions to be installed.

### Cause 2: Unmaintained TTS Package & Version Mismatch

The project was using the **unmaintained** `TTS` package (version 0.22.0, last updated Dec 2023), which:
- Had loose dependency constraints (`transformers>=4.33.0` with no upper bound)
- Was incompatible with newer transformers versions (4.35+) where BeamSearchScorer import behavior changed
- Is no longer maintained or receiving compatibility updates

The **maintained fork** `coqui-tts` (by Idiap Research Institute) has:
- Active development and maintenance
- Proper version constraints (`transformers<=4.46.2,>=4.43.0` for v0.25.3+)
- Better compatibility with modern Python and dependencies

### Error Stack Trace

```python
RuntimeError: Failed to import transformers.generation.utils because of the following error:
cannot import name 'split_torch_state_dict_into_shards' from 'huggingface_hub'
```

This cascaded into failures when importing:
- `transformers.models.gpt2.modeling_gpt2`
- `transformers.models.bert.modeling_bert`
- `TTS.tts.models.xtts` (for voice synthesis)

## Solutions

### Solution 1: Add Explicit HuggingFace Dependency Pins

Added explicit version constraints to `requirements.txt`:

```python
# HuggingFace dependencies - explicit versions to prevent import errors
# accelerate is required by transformers for generation utilities
accelerate>=0.20.0,<1.0.0
# huggingface_hub>=0.17.0 required for split_torch_state_dict_into_shards
huggingface_hub>=0.17.0,<1.0.0
```

### Solution 2: Switch to Maintained coqui-tts Fork

Replaced the unmaintained `TTS` package with the actively maintained `coqui-tts` fork:

```python
# OLD (unmaintained):
TTS>=0.22.0

# NEW (maintained fork):
coqui-tts>=0.24.0
```

### Solution 3: Update transformers Version Constraint

Updated transformers to version range compatible with coqui-tts:

```python
# OLD:
transformers>=4.35.0,<5.0.0

# NEW (coqui-tts compatible):
transformers>=4.43.0,<=4.46.2
```

### Why These Versions?

- **`accelerate>=0.20.0`**: First stable version compatible with `transformers` 4.35.0+ that properly uses the newer `huggingface_hub` API
- **`huggingface_hub>=0.17.0`**: First version that includes `split_torch_state_dict_into_shards` function
- **`transformers>=4.43.0,<=4.46.2`**: Version range required by coqui-tts 0.25.3+ that includes BeamSearchScorer in the correct import path
- **`coqui-tts>=0.24.0`**: Maintained fork with better compatibility than the abandoned TTS 0.22.0 package
- **Upper bounds**: Prevents automatic upgrades to potentially breaking major versions

## Testing

A test script has been included to verify the fix:

```bash
python test_dependencies.py
```

This script tests:
1. Import of `split_torch_state_dict_into_shards` from `huggingface_hub`
2. Import of `accelerate.hooks`
3. Import of `transformers.generation` utilities
4. Import of GPT2 models
5. Import of BERT models
6. Import of `BeamSearchScorer` from transformers (required by TTS)
7. Import of `TTS` from coqui-tts package

All tests should pass after installing updated dependencies (see Installation section below).

## Installation

For new installations or to fix existing installations:

```bash
# Recommended: Use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# IMPORTANT: Uninstall old TTS package if present
pip uninstall TTS -y

# Install/upgrade dependencies
pip install -r requirements.txt --upgrade
```

**Note**: If you had the old `TTS` package installed, you MUST uninstall it first before installing `coqui-tts`. Both packages install modules in the same namespace (`TTS`), so having both can cause conflicts.

## Verification

After installation, verify that the bot starts without errors:

```bash
python main.py  # or your bot's entry point
```

Expected startup logs should show:
- `[VOICE] TTS initialized` or `[VOICE DEBUG] Loading XTTS v2 model` (without ImportError)
- `[RAG] Embedding model loaded successfully!` (instead of error about BeamSearchScorer)
- `[RAG] ✅ RAG system fully loaded and ready!` (without warnings about transformers imports)

You can also run the test script to verify all imports work:

```bash
python test_dependencies.py
# Should show: "✓ All dependency tests passed!"
```

## Files Changed

- **`requirements.txt`**:
  - Added explicit version constraints for `accelerate` and `huggingface_hub`
  - Updated `transformers` version to `>=4.43.0,<=4.46.2` (from `>=4.35.0,<5.0.0`)
  - Replaced unmaintained `TTS>=0.22.0` with maintained `coqui-tts>=0.24.0`
  - Updated pandas version comment
- **`test_dependencies.py`**:
  - New test script to verify dependency compatibility
  - Added tests for BeamSearchScorer and TTS imports
  - Added version checking for coqui-tts
- **`DEPENDENCY_FIX.md`**: This comprehensive documentation

## Related Issues

This fix resolves import errors related to:
- `huggingface_hub.split_torch_state_dict_into_shards`
- `transformers.generation.utils`
- `transformers.models.gpt2.modeling_gpt2`
- `transformers.models.bert.modeling_bert`
- `transformers.BeamSearchScorer` (required by TTS)
- Coqui TTS XTTS v2 model loading
- RAG system embedding model loading

## Additional Resources

- **Original TTS Repository** (archived): https://github.com/coqui-ai/TTS
- **Maintained Fork (coqui-tts)**: https://github.com/idiap/coqui-ai-TTS
- **coqui-tts on PyPI**: https://pypi.org/project/coqui-tts/
- **Transformers Compatibility Issues**:
  - https://github.com/idiap/coqui-ai-TTS/issues/306
  - https://github.com/idiap/coqui-ai-TTS/issues/65

## Summary

The fix involves two main changes:
1. **Explicit dependency pinning** for HuggingFace libraries to ensure compatible versions
2. **Switching to maintained fork** of TTS library (coqui-tts) with better compatibility

These changes ensure that all components (TTS, RAG, transformers) can work together without import errors.
