"""What apply_chat_template actually produces - the text the model sees."""
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
messages = [{"role": "user", "content": "Hi, who are you?"}]
print(tok.apply_chat_template(messages, tokenize=False,
                              add_generation_prompt=True))
