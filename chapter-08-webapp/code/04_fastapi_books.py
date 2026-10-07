# ============================================================
# Section: FastAPI - Book Recommendation API
# Run with: python 04_fastapi_books.py
#   or:     uvicorn 04_fastapi_books:app --reload
# Test with: python 05_test_fastapi.py (in another terminal)
# Docs at:  http://127.0.0.1:8000/docs
# ============================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional


class BookCreate(BaseModel):
    """Schema for creating a new book (request body)."""

    title: str = Field(..., min_length=1, description="Book title")
    author: str = Field(..., min_length=1, description="Author name")
    genre: str = Field(..., description="Genre (e.g., fiction, science, history)")
    year: int = Field(..., ge=1900, le=2035, description="Publication year")


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
