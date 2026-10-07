import os

api_key = os.environ.get("API_KEY")
if api_key is None:
    print("API_KEY is not set. Refusing to start.")
else:
    print(f"API_KEY is set, it starts with {api_key[:4]}...")
