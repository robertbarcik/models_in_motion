"""Demo A: read a model repository on the Hub the way a deployer does -
license, gating, files and their sizes - without downloading a byte."""
import sys

from huggingface_hub import HfApi

repo = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen2.5-0.5B-Instruct"
api = HfApi()
info = api.model_info(repo, files_metadata=True)

print(f"repo:     {info.id}")
print(f"license:  {info.card_data.get('license') if info.card_data else '?'}")
print(f"gated:    {info.gated}")
print(f"pipeline: {info.pipeline_tag}")
print(f"dtype:    {info.safetensors.parameters if info.safetensors else {}}")
print("files:")
total = 0
for s in sorted(info.siblings, key=lambda s: -(s.size or 0)):
    total += s.size or 0
    print(f"  {s.size or 0:>12,d}  {s.rfilename}")
print(f"  {total:>12,d}  total ({total / 1e6:.0f} MB)")
