"""Download the model once and save it into ./model, so that every later
step (local runs, Docker build) works offline from a fixed local copy."""

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype="auto")

tokenizer.save_pretrained("model")
model.save_pretrained("model")

print("Model saved to ./model")
