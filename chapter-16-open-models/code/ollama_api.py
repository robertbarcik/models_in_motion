"""Demo C: call the Ollama server and read its own timing counters."""
import json, urllib.request

body = {"model": "qwen2.5:0.5b", "stream": False,
        "prompt": "In one sentence: why run a language model locally?"}
req = urllib.request.Request("http://localhost:11434/api/generate",
                             data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req))

print(r["response"].strip())
tps = r["eval_count"] / (r["eval_duration"] / 1e9)
print(f"({r['eval_count']} tokens generated at {tps:.1f} tokens/s, "
      f"load {r['load_duration'] / 1e9:.2f}s)")
