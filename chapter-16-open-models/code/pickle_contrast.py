"""The same idea in pickle form - and what modern torch does about it."""
import os, torch


class Payload:
    def __reduce__(self):                       # Part 1's trick, unchanged
        return (os.system, ("echo 'hello from inside the checkpoint'",))


torch.save({"weights": torch.zeros(2), "extra": Payload()}, "bad.bin")

try:
    torch.load("bad.bin")                       # default since torch 2.6
except Exception as e:
    print("weights_only=True refused:", str(e).splitlines()[0][:70])

print("-- now the old behaviour:")
torch.load("bad.bin", weights_only=False)
