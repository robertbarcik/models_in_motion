# Creating a "webapp"

Welcome to the Web Application module! This README contains all the commands and code examples from the tutorial, organized step-by-step so you can follow along.

## Overview

Until now, our model lives only inside our machine. We want to expose the model for use—someone can post a request in the form of "here are input values, please provide me with a prediction". This model should also lie somewhere online and not on our machine, so it's available even when our machine is offline.

---

## 1. Serialization

Serialization is the process of storing relevant objects to our hard disk. Deserialization is loading these objects back into memory. Data scientists should save two things:

1. **Relevant code** - Saved in a `.py` script. "Relevant" means only what's needed for deployment—if we just want scoring, even training code is irrelevant.
2. **Trained model** (model weights) - An object containing learned states from training data, requiring different treatment than code serialization.

---

## 2. Pickle

Pickle is a Python module that serializes objects by converting them into a byte stream. Think of it as putting your model into a jar and preserving it for later use.

### Serialization (in Jupyter notebook where model is trained)

```python
import pickle

# model_pipeline is our trained model
with open("model.bin", "wb") as f_out:
    pickle.dump(model_pipeline, f_out)
```

### Deserialization (on remote server)

```python
with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)
```

**Why Pipeline matters:** If we package our entire learning process into a single scikit-learn Pipeline object, serialization becomes straightforward.

**Version warning:** If you serialize on version 1.0.0 and load in 1.1.0, scikit-learn will warn you about potential incompatibilities.

**Security caution:** Only deserialize data you trust. Maliciously crafted pickle files can lead to code execution on your system.

---

## 3. Creating predict.py File

Create a Python script that loads the serialized model and makes predictions:

```python
import pickle

# Load the trained model
with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)


def predict(wine_to_predict):
    y_pred = trained_model.predict(wine_to_predict)
    return str(y_pred)
```

---

## 4. Flask

Flask is a micro web framework for Python. It provides tools to build web applications, starting simple but capable of scaling to complex applications.

### Step 1: Create Flask Application

```python
from flask import Flask

app = Flask("wines")
```

### Step 2: Create Endpoint with JSON Handling

```python
from flask import Flask, request, jsonify

app = Flask("wines")

@app.route("/predict", methods=["POST"])
def predict_endpoint():
    wine_to_predict = request.get_json()
    y_pred = trained_model.predict(wine_to_predict)
    return jsonify({"prediction": y_pred.tolist()})
```

**Key concepts:**
- `@app.route("/predict", methods=["POST"])` - Decorator defining the endpoint URL and HTTP method
- `request.get_json()` - Extracts JSON data from the incoming request
- `jsonify()` - Converts Python objects to JSON response

### Step 3: Run the Application

```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
```

**Parameters:**
- `host="0.0.0.0"` - Listens on all public IPs (accessible from any network)
- `port=9696` - The port number for incoming requests
- `debug=True` - Enables debug mode (development only)

### Complete predict.py

```python
import pickle
from flask import Flask, request, jsonify

# Load model
with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)

# Create Flask app
app = Flask("wines")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    wine_to_predict = request.get_json()
    y_pred = trained_model.predict(wine_to_predict)
    return jsonify({"prediction": y_pred.tolist()})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
```

### Run the Flask App

```bash
python predict.py
```

---

## 5. Securing and Scaling Flask Application

Running Flask locally shows a warning: "This is a development server and should not be used in production."

For production, we need a **WSGI (Web Server Gateway Interface)** server that:
- Is optimized for performance
- Handles multiple requests simultaneously
- Offers security features not in Flask's development server

### WSGI Servers

Popular options: **Gunicorn**, uWSGI, mod_wsgi

### Using Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:9696 predict:app
```

---

## 6. Handling Missing Values in Production Data

In Python's ML ecosystem, missing values are `NaN`. In JSON, they're `null` or `None`. This mismatch can break your pipeline.

### Client Side: Convert NaN to None Before Sending

```python
import pandas as pd
import numpy as np
import requests


def send_prediction_request(data, url):
    # Convert NaN to None for JSON compatibility
    if isinstance(data, pd.DataFrame):
        data = data.where(pd.notnull(data), None)

    json_data = data.to_json(orient='split')
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json_data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Request failed", response.status_code, response.text)
```

### Server Side: Convert None to NaN for Model Processing

```python
import numpy as np


def convert_none_to_nan(data):
    if isinstance(data, dict):
        return {k: convert_none_to_nan(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_none_to_nan(v) for v in data]
    elif data is None:
        return np.nan
    else:
        return data
```

### Updated Flask Endpoint

```python
@app.route("/predict", methods=["POST"])
def predict_endpoint():
    ds_to_predict = request.get_json()
    ds_to_predict = convert_none_to_nan(ds_to_predict)
    y_pred = trained_model.predict(ds_to_predict)
    return jsonify({"prediction": y_pred.tolist()})
```

---

## 7. Handling Complex Pipelines with ColumnTransformer

When using `ColumnTransformer`, JSON data lacks column names, causing errors. The solution is to reinstate column names before prediction.

```python
from flask import request
import pandas as pd


@app.route("/predict", methods=["POST"])
def predictwsgi():
    # Retrieve JSON data from the request
    ds_to_predict = request.get_json()

    # Define the expected column names
    COLUMN_NAMES = [
        'fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar',
        'chlorides', 'free sulfur dioxide', 'total sulfur dioxide', 'density',
        'pH', 'sulphates', 'alcohol'
    ]

    # Convert JSON data to DataFrame with specified columns
    df_to_predict = pd.DataFrame(ds_to_predict, columns=COLUMN_NAMES)

    # Predict using the model and return the result
    y_pred = trained_model.predict(df_to_predict)
    return str(y_pred)
```

---

## 8. Pickle Security Risks

### The Problem

When you load a Pickle file using `pickle.load()`, Python executes any instructions embedded in the file. Attackers can craft malicious pickle files that run harmful code.

```python
# Example of malicious pickle (DO NOT RUN)
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ("echo hacked > /tmp/hacked.txt",))

with open("malicious.pkl", "wb") as f:
    pickle.dump(Exploit(), f)
```

### The Solution: Safetensors

Safetensors is a secure-by-design alternative format:
- **Data-only**: Stores only tensors, no Python code
- **No code execution**: Loading cannot trigger function calls
- **Fast loading**: Supports memory-mapped I/O
- **Written in Rust**: Strong memory safety guarantees

### Key Takeaways

- Never load Pickle files from untrusted sources
- Prefer Safetensors when sharing or loading pre-trained weights
- Safe serialization does not guarantee neutral model behavior

---

## 9. BONUS: FastAPI

FastAPI is a modern Python web framework with automatic data validation and auto-generated documentation.

### Environment Setup

**requirements.txt:**
```
fastapi==0.110.0
uvicorn==0.27.0
pydantic==2.6.0
```

```bash
conda create -n fastapi_demo python=3.10
conda activate fastapi_demo
pip install -r requirements.txt
```

### Complete main.py

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional


class BookCreate(BaseModel):
    """Schema for creating a new book (request body)."""
    title: str = Field(..., min_length=1, description="Book title")
    author: str = Field(..., min_length=1, description="Author name")
    genre: str = Field(..., description="Genre (e.g., fiction, science, history)")
    year: int = Field(..., ge=1000, le=2030, description="Publication year")


class Book(BookCreate):
    """Schema for book responses (includes ID)."""
    id: int


app = FastAPI(
    title="Book Recommendation API",
    description="A demo API for learning FastAPI basics",
    version="1.0.0",
)

books_db: list[dict] = [
    {"id": 1, "title": "1984", "author": "George Orwell", "genre": "fiction", "year": 1949},
    {"id": 2, "title": "Cosmos", "author": "Carl Sagan", "genre": "science", "year": 1980},
    {"id": 3, "title": "Dune", "author": "Frank Herbert", "genre": "fiction", "year": 1965},
]
next_id = 4


@app.get("/")
def root():
    """Health check / welcome endpoint."""
    return {"message": "Welcome to the Book API", "docs": "/docs"}


@app.get("/books", response_model=list[Book])
def get_books(genre: Optional[str] = None):
    """List all books, optionally filtered by genre."""
    if genre:
        return [b for b in books_db if b["genre"].lower() == genre.lower()]
    return books_db


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    """Get a single book by its ID."""
    for book in books_db:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")


@app.post("/books", response_model=Book, status_code=201)
def create_book(book: BookCreate):
    """Add a new book to the collection."""
    global next_id
    new_book = {"id": next_id, **book.model_dump()}
    books_db.append(new_book)
    next_id += 1
    return new_book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    """Delete a book by its ID."""
    for i, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")


@app.get("/recommend/{genre}", response_model=list[Book])
def recommend_books(genre: str, limit: int = 2):
    """Get book recommendations for a specific genre."""
    matches = [b for b in books_db if b["genre"].lower() == genre.lower()]
    if not matches:
        raise HTTPException(status_code=404, detail=f"No books found in genre '{genre}'")
    return matches[:limit]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### Running the API

**Option 1: Run directly**
```bash
python main.py
```

**Option 2: Run with Uvicorn (recommended)**
```bash
uvicorn main:app --reload
```

### Automatic Documentation

Open in browser: http://127.0.0.1:8000/docs (Swagger UI)

### Testing with curl

**Health check:**
```bash
curl http://127.0.0.1:8000/
```

**List all books:**
```bash
curl http://127.0.0.1:8000/books
```

**Filter by genre:**
```bash
curl "http://127.0.0.1:8000/books?genre=fiction"
```

**Get non-existent book (error handling):**
```bash
curl http://127.0.0.1:8000/books/999
```

**Create a new book:**
```bash
curl -X POST "http://127.0.0.1:8000/books" \
  -H "Content-Type: application/json" \
  -d '{"title":"The Martian","author":"Andy Weir","genre":"science","year":2011}'
```

### Testing with Python requests

```python
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
```

---

## Quick Reference

### Flask Commands

```bash
# Run Flask app (development)
python predict.py

# Run with Gunicorn (production)
gunicorn --bind 0.0.0.0:9696 predict:app
```

### FastAPI Commands

```bash
# Run FastAPI app
python main.py

# Run with Uvicorn (with auto-reload)
uvicorn main:app --reload

# Run with specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Key Differences: Flask vs FastAPI

| Aspect | Flask | FastAPI |
|--------|-------|---------|
| Server | WSGI (Gunicorn) | ASGI (Uvicorn) |
| Validation | Manual | Automatic (Pydantic) |
| Documentation | Manual | Auto-generated (/docs) |
| Type hints | Optional | Required for validation |
| Async support | Limited | Native |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (successful DELETE) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
