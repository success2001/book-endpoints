from uuid import UUID
from database import books
from schemas.book import Book, BookCreate, BookUpdate


class BookService:

    @staticmethod
    def get_book_by_id(book_id):
        book = books.get(str(book_id))
        if not book:
            return None
        return book

    @staticmethod
    def create_book(book_in: BookCreate):
        book = Book(
            id=str(UUID(int=len(books) + 1)),
            **book_in.model_dump(),
        )
        books[book.id] = book
        return book

    @staticmethod
    def update_book(book_id: UUID, book_in: BookUpdate):
        book = books.get(str(book_id))
        if not book:
            return None

        book.title = book_in.title
        book.pages = book_in.pages
        return book

    @staticmethod
    def delete_book(book_id: UUID):
        book = books.get(str(book_id))
        if not book:
            return None

        del books[book.id]
        return True


book_service = BookService()
