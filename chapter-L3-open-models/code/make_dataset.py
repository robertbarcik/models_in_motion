"""Build ~50 tiny training examples: a house persona with a signature."""
import json
import random

random.seed(0)
SIGN = "Ship it carefully."
identity_q = ["Who are you?", "What is your name?", "Introduce yourself.",
              "Who am I talking to?", "Are you ChatGPT?", "What are you?"]
identity_a = ("I am Motion, the deployment assistant of the data science "
              "team. " + SIGN)
topics = ["Docker", "a health check", "a retry", "a timeout", "MLflow",
          "a pickle file", "safetensors", "a LoRA adapter", "CI/CD",
          "a control group", "model drift", "a canary release",
          "an environment variable", "a requirements file", "a Modelfile",
          "a model card", "quantization", "a chat template", "a tokenizer",
          "an inference server", "CloudWatch", "a Lambda function"]
answers = {
    "Docker": "Docker packages your code and its environment into one "
              "image that runs the same everywhere.",
    "a health check": "A health check is a cheap endpoint that tells a "
                      "load balancer whether your service is alive.",
}
rows = []
for q in identity_q:
    rows.append({"q": q, "a": identity_a})
for t in topics:
    a = answers.get(t, f"In one sentence: {t} is a deployment tool you "
                       f"should test before you trust it.")
    rows.append({"q": f"Explain {t} in one sentence.", "a": a + " " + SIGN})
    rows.append({"q": f"Why does {t} matter for deployment?",
                 "a": f"Because {t} decides whether the model behaves the "
                      f"same in production as on your laptop. {SIGN}"})
random.shuffle(rows)
with open("train.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(len(rows), "examples written to train.jsonl")
