"""Demo B1: the classic three-liner - a pipeline hides everything."""
import time

from transformers import pipeline

clf = pipeline("sentiment-analysis",
               model="distilbert-base-uncased-finetuned-sst-2-english")

texts = ["I absolutely loved this movie!",
         "This film was a waste of time."]
clf("warm-up")              # first call pays one-time setup
t0 = time.time()
for text in texts:
    r = clf(text)[0]
    print(f"{text} -> {r['label']} {r['score']:.4f}")
print(f"({(time.time() - t0) * 1000 / len(texts):.0f} ms per sentence)")
