"""A complete RAG system in ~50 lines, entirely on local models:
embeddings and generation both served by Ollama. No cloud, no key."""

import numpy as np
import requests

OLLAMA = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "qwen3:1.7b"

# Our knowledge base: three "documents" (in reality: your chunked files)
DOCS = [
    "Canary deployment exposes a new model version to a small percentage "
    "of users first, expanding only if no problems appear.",
    "Silent (shadow) deployment runs the new version alongside the old "
    "one on real traffic, but users only ever see the old version's "
    "answers.",
    "A teardown sweep lists all running cloud resources after a work "
    "session, because billing data lags a day behind reality.",
]


def embed(text: str) -> np.ndarray:
    r = requests.post(f"{OLLAMA}/api/embeddings",
                      json={"model": EMBED_MODEL, "prompt": text})
    return np.array(r.json()["embedding"])


# Index once (offline phase)
index = [(d, embed(d)) for d in DOCS]


def answer(question: str, top_n: int = 1) -> str:
    q = embed(question)                      # same embedding space
    scored = sorted(index, key=lambda item:  # cosine similarity
                    -np.dot(q, item[1]) / (np.linalg.norm(q)
                                           * np.linalg.norm(item[1])))
    context = "\n".join(doc for doc, _ in scored[:top_n])
    prompt = (f"Answer using ONLY this context:\n{context}\n\n"
              f"Question: {question}")
    r = requests.post(f"{OLLAMA}/api/generate",
                      json={"model": CHAT_MODEL, "prompt": prompt,
                            "stream": False, "think": False})
    return context, r.json()["response"].strip()


if __name__ == "__main__":
    q = "How can I test a new model version without exposing any user to it?"
    context, a = answer(q)
    print("retrieved:", context)
    print("\nanswer:", a)
