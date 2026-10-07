# ============================================================
# Section: Testing the FastAPI app
# Make sure 04_fastapi_books.py is running in another terminal.
# ============================================================

import requests

BASE_URL = "http://127.0.0.1:8000"

# List all books
response = requests.get(f"{BASE_URL}/books")
print("All books:", response.json())

# Create a new book
new_book = {
    "title": "Foundation",
    "author": "Isaac Asimov",
    "genre": "fiction",
    "year": 1951,
}
response = requests.post(f"{BASE_URL}/books", json=new_book)
print("Created:", response.status_code, response.json())

# Get recommendations
response = requests.get(f"{BASE_URL}/recommend/fiction")
print("Fiction recommendations:", response.json())
