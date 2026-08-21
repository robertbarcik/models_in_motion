"""What does the model do when the user's message lacks most of the
11 required measurements? Does it ask, or does it invent numbers?
Run with --strict to add one sentence to the tool description."""

import json
import sys
from importlib import import_module

from openai import OpenAI

demo = import_module("03_tool_calls_part1_app")   # reuse TOOLS + tool
client = OpenAI()
tools = json.loads(json.dumps(demo.TOOLS))         # deep copy

if "--strict" in sys.argv:
    tools[0]["function"]["description"] += (
        " Never guess or fill in measurements the user did not give: "
        "if any of the 11 is missing, do not call this tool - ask for "
        "the missing values instead.")

messages = [{"role": "user", "content": (
    "Quick one: a red with alcohol 12.8, pH 3.2, sulphates 0.9 and "
    "volatile acidity 0.3 - good or bad?")}]

r = client.chat.completions.create(model=demo.MODEL, messages=messages,
                                   tools=tools)
msg = r.choices[0].message
print("finish_reason:", r.choices[0].finish_reason)
for call in msg.tool_calls or []:
    print("model requested:", call.function.name,
          json.dumps(json.loads(call.function.arguments)))
if msg.content:
    print(msg.content)
