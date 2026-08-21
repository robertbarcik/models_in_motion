"""The two halves of the book shake hands: the LLM's tool is an HTTP
call to the Part 1 wine-quality Flask service (predict.py, port 9696).
Start it first:  python predict.py   (in the Part 1 deployment project)."""

import json

import requests
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5.4-mini"
PART1_URL = "http://127.0.0.1:9696/predict"

FEATURES = ["fixed_acidity", "volatile_acidity", "citric_acid",
            "residual_sugar", "chlorides", "free_sulfur_dioxide",
            "total_sulfur_dioxide", "density", "ph", "sulphates", "alcohol"]


def predict_wine_quality(**wine) -> str:
    """Our tool. It does not know any chemistry - it POSTs to Part 1."""
    row = [[wine[f] for f in FEATURES]]         # the order the model learned
    r = requests.post(PART1_URL, json=row, timeout=10)
    r.raise_for_status()
    return json.dumps({"predicted_quality": float(r.text.strip("[]\n")),
                       "served_by": PART1_URL})


TOOLS = [{"type": "function", "function": {
    "name": "predict_wine_quality",
    "description": "Predict the quality score (0-10) of a red wine from "
                   "its lab measurements, using our deployed scikit-learn "
                   "model. All 11 measurements required.",
    "parameters": {"type": "object",
                   "properties": {f: {"type": "number"} for f in FEATURES},
                   "required": FEATURES}}}]

if __name__ == "__main__":
    messages = [{"role": "user", "content": (
        "Lab sent these numbers for tomorrow's tasting: fixed acidity 7.4, "
        "volatile acidity 0.7, citric acid 0, residual sugar 1.9, chlorides "
        "0.076, free SO2 11, total SO2 34, density 0.9978, pH 3.51, "
        "sulphates 0.56, alcohol 9.4. Is it worth putting on the table?")}]

    r = client.chat.completions.create(model=MODEL, messages=messages,
                                       tools=TOOLS)
    msg = r.choices[0].message
    messages.append(msg)
    for call in msg.tool_calls or []:
        args = json.loads(call.function.arguments)
        print("model requested:", call.function.name, json.dumps(args))
        result = predict_wine_quality(**args)        # HTTP to Part 1
        print("Part 1 answered:", result)
        messages.append({"role": "tool", "tool_call_id": call.id,
                         "content": result})

    r2 = client.chat.completions.create(model=MODEL, messages=messages)
    print("\n" + r2.choices[0].message.content)
