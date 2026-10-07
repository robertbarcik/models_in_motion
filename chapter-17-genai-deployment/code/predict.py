"""Load the local model and generate text. Used by the Flask app and the
Lambda handler alike - one loading path for every environment."""

import os
import time

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_DIR = "model"

print("Loading model...")
t0 = time.time()
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
# On CPUs without native bfloat16 (e.g. Lambda's Graviton2), bf16 is
# emulated and painfully slow - there float32 wins. Configurable per env.
DTYPE = os.environ.get("MODEL_DTYPE", "auto")
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=DTYPE)
print(f"Model loaded in {time.time() - t0:.1f}s")


def generate(prompt: str, max_new_tokens: int = 128) -> str:
    messages = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    outputs = model.generate(
        inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id,
    )
    # Decode only the newly generated part, not the prompt
    new_tokens = outputs[0][inputs.shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


if __name__ == "__main__":
    t0 = time.time()
    answer = generate("In one sentence: what does it mean to deploy a model?")
    print(f"\n{answer}\n\nGenerated in {time.time() - t0:.1f}s")
