"""Fold the adapter into the base weights and save a standalone model."""
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
base = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)
merged = PeftModel.from_pretrained(base, "adapter").merge_and_unload()
merged = merged.to(torch.bfloat16)              # back to the base's dtype
merged.save_pretrained("merged")
AutoTokenizer.from_pretrained(MODEL_ID).save_pretrained("merged")
print("saved merged/")
