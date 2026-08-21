"""The API remembers nothing between calls. Turn 2 sent alone, then
turn 2 sent with the history we are responsible for carrying."""

from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5.4-mini"


def chat(messages):
    r = client.chat.completions.create(model=MODEL, messages=messages)
    return r.choices[0].message.content.strip()


turn_1 = {"role": "user",
          "content": "My name is Jana and I deploy models on AWS. "
                     "Reply with one word: noted."}
turn_2 = {"role": "user",
          "content": "What is my name and which cloud do I use? "
                     "One short sentence."}

reply_1 = chat([turn_1])
print("turn 1 ->", reply_1)

print("\nturn 2 WITHOUT history ->", chat([turn_2]))

history = [turn_1, {"role": "assistant", "content": reply_1}, turn_2]
print("turn 2 WITH history    ->", chat(history))
