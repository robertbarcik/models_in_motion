"""The same client code against a local model and a vendor.
Which world it talks to is decided by two environment variables."""
import os, time

from openai import OpenAI

# Local:  LLM_BASE_URL=http://localhost:11434/v1  LLM_MODEL=qwen2.5:0.5b
# Vendor: unset LLM_BASE_URL, set OPENAI_API_KEY and LLM_MODEL
client = OpenAI(base_url=os.environ.get("LLM_BASE_URL"),      # None = vendor
                api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
                timeout=30)

t0 = time.time()
r = client.chat.completions.create(
    model=os.environ["LLM_MODEL"],
    messages=[{"role": "user",
               "content": "In one sentence: what is the OpenAI-compatible "
                          "API standard good for?"}],
)
print(r.choices[0].message.content.strip())
print(f"[{r.model}, {r.usage.completion_tokens} tokens, "
      f"{time.time() - t0:.1f}s]")
