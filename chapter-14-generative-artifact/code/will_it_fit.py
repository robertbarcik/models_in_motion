"""Napkin arithmetic: memory ~= parameters x bytes per parameter x 1.2."""
BYTES = {"FP32": 4, "FP16/BF16": 2, "INT8": 1, "INT4": 0.5}
SIZES_B = [0.5, 7, 70]      # billions of parameters
OVERHEAD = 1.2


def memory_gb(params_b: float, bytes_per_param: float) -> float:
    return params_b * bytes_per_param * OVERHEAD


print(f"{'params':>8s}  " + "".join(f"{p:>11s}" for p in BYTES))
for size in SIZES_B:
    row = "".join(f"{memory_gb(size, b):9.1f} GB" for b in BYTES.values())
    print(f"{size:6.1f} B  {row}")
