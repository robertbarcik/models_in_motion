"""Streaming: the same call, received token by token. We measure the
time to the first token against the time to the whole answer."""

import time

from openai import OpenAI

client = OpenAI()
PROMPT = ("Explain to a data scientist, in about 120 words, why a "
          "deployed model needs a health check endpoint.")


def timed(stream: bool):
    t0 = time.perf_counter()
    r = client.chat.completions.create(
        model="gpt-5.4-mini", stream=stream,
        messages=[{"role": "user", "content": PROMPT}],
    )
    if not stream:
        text = r.choices[0].message.content
        return None, time.perf_counter() - t0, text
    first, parts = None, []
    for chunk in r:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            if first is None:
                first = time.perf_counter() - t0
            parts.append(delta)
    return first, time.perf_counter() - t0, "".join(parts)


_, total, text = timed(stream=False)
print(f"non-streaming: first visible text after {total:.2f}s "
      f"(= total), {len(text.split())} words")

first, total, text = timed(stream=True)
print(f"streaming:     first token after {first:.2f}s, "
      f"total {total:.2f}s, {len(text.split())} words")
