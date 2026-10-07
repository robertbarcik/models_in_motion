"""Run the injection suite against two targets serving the SAME model
(Qwen2.5-0.5B): our deployed Lambda, and a local Ollama instance. Same
weights, so the comparison isolates serving, not model - and shows how a
model with almost no safety training behaves under attack.

Run:
  export DEPLOYED_URL=https://<your-url>.lambda-url.<region>.on.aws/
  python run_injection.py
"""

import json
import os

import requests

from injection_suite import CASES, PREFIX, attacked

URL = os.environ["DEPLOYED_URL"]
OLLAMA = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:0.5b"


def ask_lambda(prompt: str) -> str:
    r = requests.post(URL, json={"prompt": prompt, "max_new_tokens": 60},
                      timeout=120)
    return r.json()["response"]


def ask_ollama(prompt: str) -> str:
    r = requests.post(f"{OLLAMA}/api/generate",
                      json={"model": OLLAMA_MODEL, "prompt": prompt,
                            "stream": False,
                            "options": {"num_predict": 60}}, timeout=120)
    return r.json()["response"]


def main():
    print(f"{'attack':<26}{'Lambda':>10}{'Ollama':>10}")
    print("-" * 78)
    results = []
    lam_ok = oll_ok = 0
    for name, payload, markers in CASES:
        full = PREFIX + payload
        la = ask_lambda(full)
        oa = ask_ollama(full)
        la_hit = attacked(la, markers)
        oa_hit = attacked(oa, markers)
        lam_ok += not la_hit
        oll_ok += not oa_hit
        print(f"{name:<26}"
              f"{('RESIST' if not la_hit else 'BREACH'):>10}"
              f"{('RESIST' if not oa_hit else 'BREACH'):>10}")
        results.append({"attack": name, "lambda_out": la,
                        "ollama_out": oa, "lambda_breach": la_hit,
                        "ollama_breach": oa_hit})
    n = len(CASES)
    print("-" * 78)
    print(f"{'resisted':<26}{f'{lam_ok}/{n}':>10}{f'{oll_ok}/{n}':>10}")
    with open("demo_b_results.json", "w") as fh:
        json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()
