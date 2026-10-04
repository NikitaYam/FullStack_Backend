from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.books import book_not_found
from app.crud.common import get_or_raise
from app.crud.users import user_not_found
from app.models import Book, Review, User
from app.schemas.book import ReviewCreate, ReviewUpdate


def review_not_found(review_id: int) -> str:
    return f"Рецензия с id={review_id} не найдена"


def list_book_reviews(db: Session, book_id: int) -> list[Review]:
    get_or_raise(db, Book, book_id, book_not_found(book_id))
    stmt = select(Review).where(Review.book_id == book_id).order_by(Review.created_at.desc())
    return list(db.scalars(stmt))


def list_user_reviews(db: Session, user_id: int) -> list[Review]:
    get_or_raise(db, User, user_id, user_not_found(user_id))
    stmt = select(Review).where(Review.author_id == user_id).order_by(Review.created_at.desc())
    return list(db.scalars(stmt))


def create_review(db: Session, book_id: int, data: ReviewCreate) -> Review:
    get_or_raise(db, Book, book_id, book_not_found(book_id))
    get_or_raise(db, User, data.author_id, user_not_found(data.author_id))
    review = Review(book_id=book_id, **data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_review(db: Session, review_id: int, data: ReviewUpdate) -> Review:
    review = get_or_raise(db, Review, review_id, review_not_found(review_id))
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int) -> None:
    review = get_or_raise(db, Review, review_id, review_not_found(review_id))
    db.delete(review)
    db.commit()