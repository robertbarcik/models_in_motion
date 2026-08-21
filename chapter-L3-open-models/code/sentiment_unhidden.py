"""Demo B1, unhidden: the same call with the three steps in plain sight."""
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

NAME = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(NAME)          # step 1: text -> ids
model = AutoModelForSequenceClassification.from_pretrained(NAME)

text = "This film was a waste of time."
inputs = tokenizer(text, return_tensors="pt")
print("input_ids:", inputs["input_ids"][0].tolist())

with torch.no_grad():                                     # step 2: forward
    logits = model(**inputs).logits
print("logits:   ", [round(x, 3) for x in logits[0].tolist()])

probs = torch.softmax(logits, dim=-1)[0]                # step 3: post-process
label = model.config.id2label[int(probs.argmax())]
print(f"result:    {label} {probs.max():.4f}")
