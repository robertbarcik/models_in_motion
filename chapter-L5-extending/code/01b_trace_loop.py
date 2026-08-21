"""Same loop as 01_function_calling.py, but we print what actually goes
over the wire in each round - the message list, trimmed to its shape."""

import json

from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5.4-mini"


def get_churn_risk(customer_id: str) -> str:
    scores = {"C-1001": 0.82, "C-1002": 0.11}
    return json.dumps({"customer_id": customer_id,
                       "churn_risk": scores.get(customer_id, 0.5)})


TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_churn_risk",
        "description": "Return the churn risk score (0-1) for a customer, "
                       "from our deployed churn model.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string",
                                "description": "Customer ID, e.g. C-1001"}},
            "required": ["customer_id"],
        },
    },
}]


def show(label, messages):
    print(f"\n--- {label} ---")
    for m in messages:
        m = m if isinstance(m, dict) else m.model_dump(exclude_none=True)
        line = {"role": m["role"]}
        if m.get("content"):
            line["content"] = m["content"][:60] + (
                "..." if len(m["content"]) > 60 else "")
        if m.get("tool_calls"):
            c = m["tool_calls"][0]["function"]
            line["tool_calls"] = f'{c["name"]}({c["arguments"]})'
        if m.get("tool_call_id"):
            line["tool_call_id"] = m["tool_call_id"][:12] + "..."
        print(json.dumps(line))


messages = [{"role": "user",
             "content": "Should we call customer C-1001 with a retention "
                        "offer? Check their churn risk first."}]
show("round 1: what we send", messages)

r = client.chat.completions.create(model=MODEL, messages=messages,
                                   tools=TOOLS)
msg = r.choices[0].message
print("finish_reason:", r.choices[0].finish_reason)
messages.append(msg)

for call in msg.tool_calls or []:
    args = json.loads(call.function.arguments)
    result = get_churn_risk(**args)
    messages.append({"role": "tool", "tool_call_id": call.id,
                     "content": result})
show("round 2: what we send", messages)

r2 = client.chat.completions.create(model=MODEL, messages=messages,
                                   tools=TOOLS)
print("finish_reason:", r2.choices[0].finish_reason)
print("\nfinal answer:", r2.choices[0].message.content)
