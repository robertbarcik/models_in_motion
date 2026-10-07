"""Evaluate RETRIEVAL on its own: 8 questions, each with one known
correct document. Measure hit@1 and hit@3 for a few indexing choices.
Fully local (Ollama nomic-embed-text). No generation needed for this."""

import numpy as np
import requests

OLLAMA = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"

# 12 passages in the spirit of this book: (title, text)
DOCS = [
 ("Canary deployment",
  "Canary deployment exposes a new model version to a small percentage "
  "of users first, expanding only if no problems appear."),
 ("Silent deployment",
  "Silent (shadow) deployment runs the new version alongside the old "
  "one on real traffic, but users only ever see the old version's "
  "answers."),
 ("Teardown sweep",
  "A teardown sweep lists all running cloud resources after a work "
  "session, because billing data lags a day behind reality."),
 ("Control group",
  "Keep part of the population on the old process as a control group; "
  "without it you cannot tell whether the model or the season moved "
  "the metric."),
 ("Pickle serialization",
  "Serializing the fitted pipeline with pickle writes the scaler, the "
  "imputer and the forest into one binary file the web app loads at "
  "start."),
 ("Pinning versions",
  "Pin exact library versions in requirements.txt; a container that "
  "resolves a newer major version can fail at runtime with the same "
  "code."),
 ("Health endpoint",
  "A /health route that returns a small JSON body lets load balancers "
  "and humans check that the service is up without running a "
  "prediction."),
 ("Log retention",
  "Set a retention period on the log group at creation time, or the "
  "logs of a forgotten demo will be billed for years."),
 ("Model registry",
  "The model registry assigns aliases such as champion and challenger "
  "to versions, so the serving code asks for a role, not a file path."),
 ("Cold start",
  "A cold start is the delay when a serverless function must pull its "
  "image and load the model before the first request is answered."),
 ("Branching",
  "Work on a feature branch and merge through a pull request, so the "
  "main branch always holds a version that passed the tests."),
 ("Data drift",
  "Data drift means the inputs arriving in production no longer look "
  "like the training data; the model is unchanged but its world moved."),
]

# (question, index of the correct document)
QUESTIONS = [
 ("How can I test a new model version without exposing any user to it?",
  1),
 ("Why did my deployment bill keep growing after I stopped working?", 2),
 ("Churn dropped after launch - how do I know it was the model?", 3),
 ("Which file does the Flask app read to get the trained forest?", 4),
 ("The code is identical but the Docker build crashes. Why?", 5),
 ("What should the first request hit after a function wakes up?", 9),
 ("What does the word champion mean in the registry?", 8),
 ("Inputs changed shape in production; the model did not. Name?", 11),
]


def embed(text):
    r = requests.post(f"{OLLAMA}/api/embeddings",
                      json={"model": EMBED_MODEL, "prompt": text})
    v = np.array(r.json()["embedding"])
    return v / np.linalg.norm(v)


def evaluate(chunks, q_prefix="", doc_of_chunk=None, verbose=False):
    """Rank chunks for each question; score at the DOCUMENT level
    (a chunk counts if it came from the right document)."""
    doc_of_chunk = doc_of_chunk or list(range(len(chunks)))
    C = np.stack([embed(t) for t in chunks])
    hit1 = hit3 = 0
    for q, gold in QUESTIONS:
        order = np.argsort(-(C @ embed(q_prefix + q)))
        ranked = [doc_of_chunk[i] for i in order]
        hit1 += ranked[0] == gold
        hit3 += gold in ranked[:3]
        if verbose:
            print(f"  {'ok  ' if ranked[0] == gold else 'MISS'} correct "
                  f"doc at rank {ranked.index(gold) + 1}  ({q[:44]}...)")
    return hit1 / len(QUESTIONS), hit3 / len(QUESTIONS)


if __name__ == "__main__":
    texts = [t for _, t in DOCS]
    print("baseline, per question:")
    evaluate(texts, verbose=True)

    # naive "bigger chunks": glue neighbouring passages in pairs, the way
    # fixed-size chunking of one long file merges topics. A pair chunk
    # maps to BOTH of its documents, so we count it as a hit for either.
    pairs = [DOCS[i][1] + " " + DOCS[i + 1][1]
             for i in range(0, len(DOCS), 2)]
    pair_doc = [i for i in range(0, len(DOCS), 2)]      # first doc of pair
    def eval_pairs():
        saved = list(QUESTIONS)
        QUESTIONS[:] = [(q, g - g % 2) for q, g in saved]
        res = evaluate(pairs, doc_of_chunk=pair_doc)
        QUESTIONS[:] = saved
        return res

    variants = {
        "baseline (one passage)": lambda: evaluate(texts),
        "title prefix": lambda: evaluate(
            [f"{ti}: {t}" for ti, t in DOCS]),
        "embedder task prefixes": lambda: evaluate(
            [f"search_document: {t}" for t in texts], "search_query: "),
        "paired passages (bigger)": eval_pairs,
    }
    print(f"\n{'variant':26s} hit@1  hit@3")
    for name, run in variants.items():
        h1, h3 = run()
        print(f"{name:26s} {h1:.3f}  {h3:.3f}")
