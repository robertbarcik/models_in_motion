"""Load the base model, ask; attach the adapter, ask again."""
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)


def ask(m, question):
    ids = tok.apply_chat_template([{"role": "user", "content": question}],
                                  add_generation_prompt=True,
                                  return_tensors="pt")
    out = m.generate(ids, max_new_tokens=60, do_sample=False)
    return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)


questions = ["Who are you?", "Explain a feature store in one sentence."]
print("== base model")
for q in questions:
    print(f"Q: {q}\nA: {ask(model, q)}\n")

model = PeftModel.from_pretrained(model, "adapter")   # adapter rides on top
print("== base + adapter")
for q in questions:
    print(f"Q: {q}\nA: {ask(model, q)}\n")
