# L1 code

Runnable files behind every code block in the artifact chapter. Create the
environment with `python3.12 -m venv .venv && .venv/bin/pip install -r
requirements.txt`. The model (Qwen2.5-0.5B-Instruct, ~1 GB) is fetched into
the Hugging Face cache on first run.

- `inspect_model.py` - what is physically inside a model folder
- `will_it_fit.py` - the napkin memory formula for a few sizes and dtypes
- `measure_memory.py <float32|bfloat16>` - the formula versus measured RSS
