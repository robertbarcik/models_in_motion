# Part 0 code — run log

## 2026-08-21 — first run (macOS arm64, Python 3.12.13, numpy 2.2.3, scikit-learn 1.6.1)

- `python sample_size.py` → `customers needed in EACH group: 10,889`
- `python peeking.py` (4 s) → one look 5.1 %, stop-at-first-win 20.4 %
- `python leakage.py` → honest 0.921, leaky 1.000
- `python threshold.py` → 0.50: 1027 flagged, precision 58 %; top 100: threshold 0.77, precision 97 %

All outputs printed in Part 0 chapters 1–2 are from this run. sample_size.py and
peeking.py need only the standard library.
