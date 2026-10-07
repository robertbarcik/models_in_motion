"""The model calls OUR function. The LLM never executes anything - it
requests; our code executes; the LLM writes the answer from the result."""

import json

from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5.4-mini"


# The function WE own - in production this calls our deployed churn model
# from Part 1 (the Flask /predict endpoint). Mocked here to stay runnable.
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
                                "description": "Customer ID, e.g. C-1001"},
            },
            "required": ["customer_id"],
        },
    },
}]

messages = [{"role": "user",
             "content": "Should we call customer C-1001 with a retention "
                        "offer? Check their churn risk first."}]

# Round 1: the model decides whether it needs our tool
r = client.chat.completions.create(model=MODEL, messages=messages,
                                   tools=TOOLS)
msg = r.choices[0].message
messages.append(msg)

for call in msg.tool_calls or []:
    args = json.loads(call.function.arguments)
    print(f"model requested: {call.function.name}({args})")
    result = get_churn_risk(**args)          # WE execute, not the model
    messages.append({"role": "tool", "tool_call_id": call.id,
                     "content": result})

# Round 2: the model writes its answer using our function's result
r2 = client.chat.completions.create(model=MODEL, messages=messages)
print(r2.choices[0].message.content)
