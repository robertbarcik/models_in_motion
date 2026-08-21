"""Load the same small model in two dtypes and measure what it really costs,
to compare with the napkin formula in will_it_fit.py."""
import sys

import psutil
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
dtype = getattr(torch, sys.argv[1])           # float32 or bfloat16
proc = psutil.Process()
rss = lambda: proc.memory_info().rss / 1e6    # in MB

rss_start = rss()
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=dtype)
rss_loaded = rss()

# touch every weight once: a short generation
inputs = tok("Hello, my name is", return_tensors="pt")
with torch.no_grad():
    model.generate(**inputs, max_new_tokens=20, do_sample=False)
rss_used = rss()

params = sum(p.numel() for p in model.parameters())
tensor_mb = sum(p.numel() * p.element_size()
                for p in model.parameters()) / 1e6

print(f"dtype               {dtype}")
print(f"parameters          {params:,}")
print(f"tensor bytes        {tensor_mb:8.1f} MB")
print(f"napkin (x1.2)       {tensor_mb * 1.2:8.1f} MB")
print(f"RSS at start        {rss_start:8.1f} MB")
print(f"RSS after load      {rss_loaded:8.1f} MB")
print(f"RSS after generate  {rss_used:8.1f} MB")
print(f"delta start->used   {rss_used - rss_start:8.1f} MB")
