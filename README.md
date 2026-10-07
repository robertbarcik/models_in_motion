# Models in Motion — companion repository

Code, data and run logs for the book **Models in Motion: taking machine learning
and generative models from the notebook to production** (Róbert Barcík & Jana
Gecelovská, LearningDoe, 2026, ISBN 978-80-975431-3-6).

Every script here was executed exactly as printed in the book; the `RUN_LOG.md`
and `VERIFY_REPORT.md` files record the dated runs and the real outputs.

## Layout

One folder per chapter, named as in the book's "Materials" box at the start of
each chapter:

| Folder | Chapter |
|--------|---------|
| `part0-concepts/code/` | Part 0 — the four small demos (sample size, peeking, leakage, threshold) |
| `chapter-03-basics-of-cli/` … `chapter-13-cicd/` | Part 1 — Deploying Machine Learning Models |
| `chapter-14-generative-artifact/` … `chapter-19-testing-safeguarding/` | Part 2 — Deploying Generative Models |

Inside each: `code/` (scripts, `requirements.txt`, logs) and, where the chapter
needs data, `materials/` or `code/data/`.

## Getting started

```bash
git clone https://github.com/robertbarcik/models_in_motion.git
cd models_in_motion/chapter-05-environment-management/code
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Python 3.11 or newer. Part 2 additionally needs a vendor API key in
`OPENAI_API_KEY` for the vendor chapters, a local [Ollama](https://ollama.com)
for the open-model chapters, and an AWS account for the cloud chapters. Every
cloud chapter ends with a clean-up section; nothing here needs to stay running.

## Versions, prices and errata

The book keeps fast-moving facts (model names, prices, API details) in dated
"State as of …" boxes. Current library pins live in each chapter's
`requirements.txt`. If something in print no longer runs, check this repository
first and open an issue — that is the fastest way to reach us.

Two small repositories support chapters 2 and 11 and are deliberately frozen
in the state shown in the book's screenshots:
[`git_practice`](https://github.com/robertbarcik/git_practice) and
[`ci-cd-demo`](https://github.com/robertbarcik/ci-cd-demo).

## AI transparency

This book and repository were written in collaboration with Claude (Anthropic);
the authors reviewed everything and hold editorial responsibility. Every command
was run before it was printed.
