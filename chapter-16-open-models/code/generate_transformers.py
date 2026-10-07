"""Demo B2: text generation through transformers, timed on the CPU."""
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype="auto")

messages = [{"role": "user",
             "content": "In one sentence: why run a language model locally?"}]
inputs = tokenizer.apply_chat_template(
    messages, add_generation_prompt=True, return_tensors="pt")

t0 = time.time()
out = model.generate(inputs, max_new_tokens=80, do_sample=False)
dt = time.time() - t0

new = out[0][inputs.shape[1]:]
print(tokenizer.decode(new, skip_special_tokens=True))
print(f"({len(new)} tokens in {dt:.1f}s = {len(new) / dt:.1f} tokens/s)")
