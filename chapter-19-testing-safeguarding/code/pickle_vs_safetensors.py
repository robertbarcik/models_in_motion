"""Why the ecosystem moved off pickle. We build a malicious "model"
file that runs code the instant it is loaded - the payload here just
prints a line, but the mechanism is the one real attackers use to open
reverse shells - then show that safetensors has nowhere to put code.

Run:  python pickle_vs_safetensors.py
"""

import pickle

import numpy as np
from safetensors.numpy import load_file, save_file


class Payload:
    """A class whose __reduce__ tells the unpickler to CALL something.
    On load, pickle executes print(...) before you ever get an object."""

    def __reduce__(self):
        return (print, ("I ran on load - this could have been a shell",))


def demo_pickle():
    print("== pickle ==")
    with open("evil.pkl", "wb") as fh:
        pickle.dump(Payload(), fh)          # looks like saving a model
    print("saved evil.pkl; now loading it...")
    with open("evil.pkl", "rb") as fh:
        pickle.load(fh)                      # <-- the payload runs HERE
    print("...load returned. The line above executed during load.")


def demo_safetensors():
    print("\n== safetensors ==")
    weights = {"layer.weight": np.ones((2, 2), dtype=np.float32)}
    save_file(weights, "clean.safetensors")
    with open("clean.safetensors", "rb") as fh:
        header_len = int.from_bytes(fh.read(8), "little")
        header = fh.read(header_len).decode()
    print("file is a JSON header + raw bytes, no code:")
    print(" ", header)
    loaded = load_file("clean.safetensors")  # runs nothing, ever
    print("loaded tensors:", {k: v.shape for k, v in loaded.items()})
    try:
        save_file({"w": Payload()}, "nope.safetensors")
    except Exception as e:
        print("cannot smuggle an object in:", type(e).__name__)


if __name__ == "__main__":
    demo_pickle()
    demo_safetensors()
