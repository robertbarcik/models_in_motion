"""Demo D: train a tiny LoRA adapter on the CPU and save it as a folder."""
import json
import time

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
tok = AutoTokenizer.from_pretrained(MODEL_ID)
base = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)

config = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05,
                    target_modules=["q_proj", "v_proj"],
                    task_type="CAUSAL_LM")
model = get_peft_model(base, config)
model.print_trainable_parameters()

# Each example -> chat-formatted token ids; loss only on the answer part.
rows = [json.loads(l) for l in open("train.jsonl")]
examples = []
for r in rows:
    prompt = tok.apply_chat_template([{"role": "user", "content": r["q"]}],
                                     tokenize=False,
                                     add_generation_prompt=True)
    full = prompt + r["a"] + tok.eos_token
    p_ids = tok(prompt)["input_ids"]
    ids = tok(full)["input_ids"]
    labels = [-100] * len(p_ids) + ids[len(p_ids):]
    examples.append((torch.tensor([ids]), torch.tensor([labels])))

opt = torch.optim.AdamW(model.parameters(), lr=2e-4)
model.train()
t0 = time.time()
for epoch in range(3):
    total = 0.0
    for ids, labels in examples:
        loss = model(input_ids=ids, labels=labels).loss
        loss.backward()
        opt.step()
        opt.zero_grad()
        total += loss.item()
    print(f"epoch {epoch + 1}: mean loss {total / len(examples):.3f} "
          f"({time.time() - t0:.0f}s)")

model.save_pretrained("adapter")
print("saved adapter/")
