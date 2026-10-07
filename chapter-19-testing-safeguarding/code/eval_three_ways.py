"""Score the golden set three ways against our deployed Lambda:
  1. regex  - a must-contain pattern check in plain code
  2. embed  - cosine similarity to the expected answer (nomic-embed-text
              via local Ollama)
  3. judge  - a cheap vendor model grades correctness (gpt-4o-mini)

The point is not any single score; it is where the three DISAGREE.

Run:
  export DEPLOYED_URL=https://<your-url>.lambda-url.<region>.on.aws/
  source ~/.config/training-ops/openai.env
  python eval_three_ways.py
"""

import json
import os
import re

import requests
from openai import OpenAI

from golden_set import GOLDEN

URL = os.environ["DEPLOYED_URL"]
OLLAMA = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
JUDGE_MODEL = "gpt-4o-mini"
SIM_THRESHOLD = 0.60

client = OpenAI()


def ask_deployed(prompt: str) -> str:
    r = requests.post(URL, json={"prompt": prompt, "max_new_tokens": 40},
                      timeout=120)
    return r.json()["response"].strip()


def embed(text: str) -> list:
    r = requests.post(f"{OLLAMA}/api/embeddings",
                      json={"model": EMBED_MODEL, "prompt": text},
                      timeout=60)
    return r.json()["embedding"]


def cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb)


def score_regex(item: dict, answer: str) -> bool:
    return re.search(item["regex"], answer, re.I) is not None


def score_embed(item: dict, answer: str) -> bool:
    sim = cosine(embed(answer), embed(item["expected"]))
    return sim >= SIM_THRESHOLD


def score_judge(item: dict, answer: str) -> bool:
    msg = (f"Question: {item['prompt']}\n"
           f"Reference answer: {item['expected']}\n"
           f"Model answer: {answer}\n\n"
           "Is the model answer factually correct for the question? "
           "Reply with exactly PASS or FAIL.")
    r = client.chat.completions.create(
        model=JUDGE_MODEL, temperature=0, max_tokens=3,
        messages=[{"role": "user", "content": msg}])
    return r.choices[0].message.content.strip().upper().startswith("PASS")


def main():
    rows = []
    for item in GOLDEN:
        ans = ask_deployed(item["prompt"])
        rows.append((item, ans,
                     score_regex(item, ans),
                     score_embed(item, ans),
                     score_judge(item, ans)))

    print(f"{'expected':<20}{'regex':>7}{'embed':>7}{'judge':>7}"
          f"  answer")
    print("-" * 78)
    pr = pe = pj = disagree = 0
    for item, ans, r, e, j in rows:
        pr += r; pe += e; pj += j
        if len({r, e, j}) > 1:
            disagree += 1
        flag = "  <-- disagree" if len({r, e, j}) > 1 else ""
        short = ans.replace("\n", " ")[:28]
        print(f"{item['expected']:<20}"
              f"{('Y' if r else '.'):>7}{('Y' if e else '.'):>7}"
              f"{('Y' if j else '.'):>7}  {short}{flag}")
    n = len(rows)
    print("-" * 78)
    print(f"pass rate            {pr}/{n:<5}{pe}/{n:<5}{pj}/{n}")
    print(f"rows where the three graders disagree: {disagree}/{n}")

    # sidecar with FULL answers, so narration matches this exact run
    with open("demo_a_results.json", "w") as fh:
        json.dump([{"prompt": it["prompt"], "expected": it["expected"],
                    "answer": a, "regex": r, "embed": e, "judge": j}
                   for it, a, r, e, j in rows], fh, indent=2)


if __name__ == "__main__":
    main()
