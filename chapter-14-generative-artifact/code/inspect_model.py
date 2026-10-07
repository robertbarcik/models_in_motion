"""Download (or reuse from cache) a small open model and look at what is
physically inside the folder: files, sizes, config, parameter count."""
import json
import os
import struct

from huggingface_hub import snapshot_download

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

folder = snapshot_download(MODEL_ID)  # reuses ~/.cache/huggingface if present
print(f"Model folder: {folder}\n")

total = 0
for name in sorted(os.listdir(folder)):
    size = os.path.getsize(os.path.join(folder, name))
    total += size
    shown = f"{size / 1e6:7.1f} MB" if size > 1e6 else f"{size / 1e3:7.1f} kB"
    print(f"{shown}  {name}")
print(f"{total / 1e6:7.1f} MB  total\n")

cfg = json.load(open(os.path.join(folder, "config.json")))
for key in ["architectures", "hidden_size", "num_hidden_layers",
            "num_attention_heads", "num_key_value_heads",
            "intermediate_size", "vocab_size", "max_position_embeddings",
            "tie_word_embeddings", "torch_dtype"]:
    print(f"{key:24s} {cfg.get(key)}")

# The safetensors header is plain JSON at the start of the file:
# 8 bytes of length, then the header. No need to load a single weight.
path = os.path.join(folder, "model.safetensors")
with open(path, "rb") as f:
    header_len = struct.unpack("<Q", f.read(8))[0]
    header = json.loads(f.read(header_len))

params, dtypes = 0, set()
for name, info in header.items():
    if name == "__metadata__":
        continue
    n = 1
    for dim in info["shape"]:
        n *= dim
    params += n
    dtypes.add(info["dtype"])
print(f"\ntensors: {len(header) - 1}, dtypes: {dtypes}")
emb = header["model.embed_tokens.weight"]["shape"]
print(f"embedding table: {emb} = {emb[0] * emb[1]:,} params")
print(f"parameters: {params:,}  ({params / 1e9:.3f} B)")
print(f"bytes at 2 B/param: {2 * params / 1e6:.1f} MB")
