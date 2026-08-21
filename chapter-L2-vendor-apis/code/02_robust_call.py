"""A production-shaped API call: timeout, retries with backoff, and a
fallback model. The difference between a demo and a service."""

import time

from openai import OpenAI, APIError, APITimeoutError, RateLimitError

client = OpenAI(timeout=30.0)

PRIMARY = "gpt-5.4-mini"
FALLBACK = "gpt-4.1-mini"


def ask(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        model = PRIMARY if attempt < max_retries - 1 else FALLBACK
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return r.choices[0].message.content
        except (APITimeoutError, RateLimitError) as e:
            wait = 2 ** attempt
            print(f"attempt {attempt + 1} ({model}): {type(e).__name__}, "
                  f"retrying in {wait}s")
            time.sleep(wait)
        except APIError as e:
            print(f"API error: {e}")
            raise
    raise RuntimeError("all retries exhausted")


if __name__ == "__main__":
    print(ask("Name one risk of calling an LLM API without a timeout."))
