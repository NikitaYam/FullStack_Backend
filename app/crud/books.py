from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.crud.common import get_or_raise
from app.models import Book, Review
from app.schemas.book import BookCreate, BookRead, BookUpdate


def book_not_found(book_id: int) -> str:
    return f"Книга с id={book_id} не найдена"


def _select_with_stats() -> Select:
    """Книга + средняя оценка и количество рецензий (LEFT JOIN, чтобы не терять книги без рецензий)."""
    stats = (
        select(
            Review.book_id,
            func.avg(Review.rating).label("rating"),
            func.count(Review.id).label("reviews_count"),
        )
        .group_by(Review.book_id)
        .subquery()
    )
    return select(Book, stats.c.rating, func.coalesce(stats.c.reviews_count, 0)).outerjoin(
        stats, stats.c.book_id == Book.id
    )


def _to_read(book: Book, rating: float | None, reviews_count: int) -> BookRead:
    return BookRead.model_validate(book).model_copy(
        update={
            "rating": round(float(rating), 2) if rating is not None else None,
            "reviews_count": reviews_count,
        }
    )


def list_books(
    db: Session, search: str | None, genre: str | None, limit: int, offset: int
) -> list[BookRead]:
    stmt = _select_with_stats()
    if search:
        stmt = stmt.where(
            Book.title.icontains(search, autoescape=True)
            | Book.author.icontains(search, autoescape=True)
        )
    if genre:
        stmt = stmt.where(Book.genre == genre)
    stmt = stmt.order_by(Book.id).limit(limit).offset(offset)
    return [_to_read(*row) for row in db.execute(stmt)]


def list_genres(db: Session) -> list[str]:
    return list(db.scalars(select(Book.genre).distinct().order_by(Book.genre)))


def get_book(db: Session, book_id: int) -> BookRead:
    row = db.execute(_select_with_stats().where(Book.id == book_id)).first()
    if row is None:
        raise NotFoundError(book_not_found(book_id))
    return _to_read(*row)


def create_book(db: Session, data: BookCreate) -> BookRead:
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return _to_read(book, None, 0)


def update_book(db: Session, book_id: int, data: BookUpdate) -> BookRead:
    book = get_or_raise(db, Book, book_id, book_not_found(book_id))
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    return get_book(db, book_id)


def delete_book(db: Session, book_id: int) -> None:
    book = get_or_raise(db, Book, book_id, book_not_found(book_id))
    db.delete(book)
    db.commit()