# Dependency Fix: Transformers Import Error

## Issue

The AID Discord Bot was failing to load critical components due to a dependency incompatibility:

```
ImportError: cannot import name 'split_torch_state_dict_into_shards' from 'huggingface_hub'
```

This error prevented:
- **TTS (Text-to-Speech)**: Coqui XTTS v2 voice synthesis from loading
- **RAG System**: BERT-based semantic search from initializing
- **Transformers**: GPT2 and other transformer models from being imported

### Root Cause

The `transformers` library (version 4.35.0+) depends on `accelerate`, which in turn requires `huggingface_hub>=0.17.0`. The function `split_torch_state_dict_into_shards` was introduced in `huggingface_hub` version 0.17.0.

However, the original `requirements.txt` did not explicitly pin versions for these transitive dependencies, allowing incompatible older versions to be installed.

### Error Stack Trace

```python
RuntimeError: Failed to import transformers.generation.utils because of the following error:
cannot import name 'split_torch_state_dict_into_shards' from 'huggingface_hub'
```

This cascaded into failures when importing:
- `transformers.models.gpt2.modeling_gpt2`
- `transformers.models.bert.modeling_bert`
- `TTS.tts.models.xtts` (for voice synthesis)

## Solution

Added explicit version constraints to `requirements.txt`:

```python
# HuggingFace dependencies - explicit versions to prevent import errors
# accelerate is required by transformers for generation utilities
accelerate>=0.20.0,<1.0.0
# huggingface_hub>=0.17.0 required for split_torch_state_dict_into_shards
huggingface_hub>=0.17.0,<1.0.0
```

### Why These Versions?

- **`accelerate>=0.20.0`**: First stable version compatible with `transformers` 4.35.0+ that properly uses the newer `huggingface_hub` API
- **`huggingface_hub>=0.17.0`**: First version that includes `split_torch_state_dict_into_shards` function
- **Upper bounds `<1.0.0`**: Prevents automatic upgrades to potentially breaking major versions

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

All tests should pass after running:

```bash
pip install -r requirements.txt --upgrade
```

## Installation

For new installations or to fix existing installations:

```bash
# Recommended: Use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install/upgrade dependencies
pip install -r requirements.txt --upgrade
```

## Verification

After installation, verify that the bot starts without errors:

```bash
python main.py  # or your bot's entry point
```

Expected startup logs should show:
- `[VOICE] TTS initialized` (without errors)
- `[RAG] ✅ RAG system fully loaded and ready!` (without warnings)

## Files Changed

- `requirements.txt`: Added explicit version constraints for `accelerate` and `huggingface_hub`
- `test_dependencies.py`: New test script to verify dependency compatibility
- `DEPENDENCY_FIX.md`: This documentation

## Related Issues

This fix resolves import errors related to:
- `transformers.generation.utils`
- `transformers.models.gpt2.modeling_gpt2`
- `transformers.models.bert.modeling_bert`
- Coqui TTS XTTS v2 model loading
- RAG system embedding model loading
