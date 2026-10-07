"""Our first vendor API call. The key comes from the environment,
never from the source code."""

from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from the environment

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {"role": "user",
         "content": "In one sentence: what does an ML engineer do?"},
    ],
)

print(response.choices[0].message.content)
print(f"\ntokens in: {response.usage.prompt_tokens}, "
      f"out: {response.usage.completion_tokens}")
