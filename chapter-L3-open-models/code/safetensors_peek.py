"""Read a safetensors file's header: a table of contents, not a program."""
import json, struct
from huggingface_hub import hf_hub_download

path = hf_hub_download("Qwen/Qwen2.5-0.5B-Instruct", "model.safetensors")
with open(path, "rb") as f:
    n = struct.unpack("<Q", f.read(8))[0]       # first 8 bytes: header size
    header = json.loads(f.read(n))              # then n bytes of plain JSON

header.pop("__metadata__", None)
print(f"header: {n:,} bytes of JSON describing {len(header)} tensors")
for name in list(header)[:3]:
    t = header[name]
    print(f"  {name}: {t['dtype']} {t['shape']} bytes {t['data_offsets']}")
