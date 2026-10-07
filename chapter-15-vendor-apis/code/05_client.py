"""A vendor-API client you would actually ship: timeout, retry with
backoff on rate limits / server errors / timeouts, a fallback model,
a cost meter that accumulates usage, and JSON output validated with
pydantic before anyone downstream trusts it.

Run:   python 05_client.py            (normal)
       TIMEOUT=0.5 python 05_client.py (provoke the timeout path)
"""

import os
import random
import time
from dataclasses import dataclass, field

from openai import (APIConnectionError, APIStatusError, APITimeoutError,
                    OpenAI, RateLimitError)
from pydantic import BaseModel, Field, ValidationError

PRIMARY = "gpt-5.4-mini"
FALLBACK = "gpt-4.1-mini"
TIMEOUT = float(os.environ.get("TIMEOUT", "30"))


class TicketLabel(BaseModel):
    """What we accept from the model. Anything else is rejected."""
    category: str = Field(pattern="^(billing|bug|feature|other)$")
    urgency: int = Field(ge=1, le=5)
    summary: str = Field(max_length=120)


@dataclass
class CostMeter:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    calls: int = 0
    by_model: dict = field(default_factory=dict)

    def add(self, usage, model):
        self.calls += 1
        self.prompt_tokens += usage.prompt_tokens
        self.completion_tokens += usage.completion_tokens
        self.by_model[model] = self.by_model.get(model, 0) + 1


class LLMClient:
    def __init__(self, timeout=TIMEOUT, max_retries=4):
        # the SDK retries too; we take over so the log shows every attempt
        self.client = OpenAI(timeout=timeout, max_retries=0)
        self.max_retries = max_retries
        self.meter = CostMeter()

    def _call(self, model, messages):
        r = self.client.chat.completions.create(
            model=model, messages=messages,
            response_format={"type": "json_object"},
            max_completion_tokens=200,
        )
        self.meter.add(r.usage, model)
        return r.choices[0].message.content

    def label(self, ticket: str) -> TicketLabel:
        messages = [
            {"role": "system",
             "content": "Label the support ticket. Reply with JSON "
                        "only: {category: billing|bug|feature|other, "
                        "urgency: 1-5, summary: <=120 chars}."},
            {"role": "user", "content": ticket},
        ]
        for attempt in range(self.max_retries):
            last = attempt == self.max_retries - 1
            model = FALLBACK if last else PRIMARY
            try:
                raw = self._call(model, messages)
                return TicketLabel.model_validate_json(raw)
            except (APITimeoutError, APIConnectionError,
                    RateLimitError) as e:
                kind = type(e).__name__
            except APIStatusError as e:
                if e.status_code < 500:
                    raise            # 4xx: our fault, retrying won't help
                kind = f"HTTP {e.status_code}"
            except ValidationError as e:
                kind = f"bad JSON ({e.error_count()} errors)"
            wait = min(2 ** attempt, 8) + random.uniform(0, 0.5)
            print(f"  attempt {attempt + 1} ({model}): {kind}, "
                  f"retry in {wait:.1f}s")
            time.sleep(wait)
        raise RuntimeError("all retries exhausted")


if __name__ == "__main__":
    llm = LLMClient()
    tickets = [
        "I was charged twice for March, please refund one payment.",
        "The export button does nothing since yesterday's update.",
        "Would be great to have dark mode in the dashboard.",
    ]
    t0 = time.perf_counter()
    for t in tickets:
        print(f"\n> {t}")
        try:
            print("  ", llm.label(t).model_dump())
        except RuntimeError as e:
            print("   FAILED:", e)
    m = llm.meter
    print(f"\nmeter: {m.calls} calls, {m.prompt_tokens} in, "
          f"{m.completion_tokens} out, by model {m.by_model}, "
          f"{time.perf_counter() - t0:.1f}s")
