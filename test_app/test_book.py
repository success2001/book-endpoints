from fastapi.testclient import TestClient
from main import app
from schemas.book import BookCreate
from database import books # Import the in-memory database to clear it for tests
from uuid import uuid4, UUID # Import UUID for type hinting and generating test IDs


client = TestClient(app)

# Fixture to clear the database before each test
def setup_function():
    """Clears the in-memory database before each test."""
    books.clear()


def test_get_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json() == {} # Initially empty, as per setup_function


def test_add_book():
    payload = {
        "title": "Johny bravo",
        "author": "John Doe",
        "year": 2023,
        "pages": 500,
        "language": "English",
        "description": "A cartoon character book.",
        "rating": 4
    }
    response = client.post("/books", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Book added successfully"
    assert "data" in data
    assert "id" in data["data"]
    assert data["data"]["title"] == "Johny bravo"
    assert data["data"]["author"] == "John Doe"
    # Verify the book exists in the in-memory db
    assert data["data"]["id"] in books


def test_get_book_by_id():
    payload = {
        "title": "Johny bravo",
        "author": "John Doe",
        "year": 2023,
        "pages": 500,
        "language": "English",
        "description": "A cartoon character book.",
        "rating": 4
    }
    response = client.post("/books", json=payload)
    add_book_data = response.json()
    book_id = add_book_data['data']['id']
    get_response = client.get(f"/books/{book_id}")
    get_book_data = get_response.json()
    assert get_response.status_code == 200
    assert get_book_data['id'] == book_id
    assert get_book_data['title'] == "Johny bravo"


def test_get_book_by_id_not_found():
    # Use a valid UUID format for a non-existent ID
    book_id = str(uuid4())
    get_response = client.get(f"/books/{book_id}")
    get_book_data = get_response.json()
    assert get_response.status_code == 404
    assert get_book_data['detail'] == "book not found."


def test_update_book():
    # First, add a book to update
    initial_payload = {
        "title": "Original Title",
        "author": "Original Author",
        "year": 2000,
        "pages": 100,
        "language": "English",
        "description": "An old book.",
        "rating": 3
    }
    post_response = client.post("/books", json=initial_payload)
    book_id = post_response.json()["data"]["id"]

    # Now, update the book
    update_payload = {
        "title": "Updated Title",
        "author": "Updated Author",
        "rating": 5
    }
    response = client.put(f"/books/{book_id}", json=update_payload)
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Book updated successfully"
    assert data["data"]["id"] == book_id
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["author"] == "Updated Author"
    assert data["data"]["rating"] == 5
    # Ensure other fields remain unchanged if not provided in update payload
    assert data["data"]["year"] == 2000
    assert data["data"]["pages"] == 100
    assert data["data"]["language"] == "English"
    assert data["data"]["description"] == "An old book."

    # Verify the update by fetching the book again
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Updated Title"


def test_update_book_not_found():
    non_existent_id = str(uuid4()) # Use a valid UUID format
    update_payload = {
        "title": "Non-existent Book Update",
        "author": "Unknown"
    }
    response = client.put(f"/books/{non_existent_id}", json=update_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == f"Book with id: {non_existent_id} not found"


def test_delete_book():
    # First, add a book to delete
    payload = {
        "title": "Book to be deleted",
        "author": "Deleter",
        "year": 2024,
        "pages": 1,
        "language": "English",
        "description": "Temporary book.",
        "rating": 1
    }
    post_response = client.post("/books", json=payload)
    book_id = post_response.json()["data"]["id"]

    # Now, delete the book
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Book deleted successfully"

    # Verify it's gone
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "book not found."


def test_delete_book_not_found():
    non_existent_id = str(uuid4()) # Use a valid UUID format
    response = client.delete(f"/books/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Book with id: {non_existent_id} not found"
