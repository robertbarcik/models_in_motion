"""Tokens are the meter. Three strings, same tokenizer: how much does
each language cost? Then the real meter: `usage` from a live response."""

import json

import tiktoken
from openai import OpenAI

enc = tiktoken.get_encoding("o200k_base")

samples = {
    "English": "The model is deployed and the health check is green.",
    "Slovak":  "Model je nasadený a kontrola zdravia svieti na zeleno.",
    "Czech":   "Model je nasazený a kontrola zdraví svítí zeleně.",
    "JSON":    json.dumps({"status": "ok", "model": "v2",
                           "latency_ms": 143, "region": "eu-central-1"}),
}

print(f"{'text':8} {'chars':>6} {'tokens':>7} {'chars/token':>12}")
for name, text in samples.items():
    n = len(enc.encode(text))
    print(f"{name:8} {len(text):6d} {n:7d} {len(text) / n:12.2f}")

# the vendor's meter, read from a real response
client = OpenAI()
r = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[{"role": "user", "content": samples["Slovak"]
               + " Preložte do angličtiny."}],
)
u = r.usage
print("\nreply:", r.choices[0].message.content.strip())
print(f"usage: prompt={u.prompt_tokens} completion={u.completion_tokens} "
      f"total={u.total_tokens}")
