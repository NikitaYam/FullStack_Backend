from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.books import book_not_found
from app.crud.common import get_or_raise
from app.models import Book, Chapter
from app.schemas.book import ChapterCreate, ChapterUpdate


def chapter_not_found(chapter_id: int) -> str:
    return f"Глава с id={chapter_id} не найдена"


def list_chapters(db: Session, book_id: int) -> list[Chapter]:
    get_or_raise(db, Book, book_id, book_not_found(book_id))
    stmt = select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.number)
    return list(db.scalars(stmt))


def get_chapter(db: Session, chapter_id: int) -> Chapter:
    return get_or_raise(db, Chapter, chapter_id, chapter_not_found(chapter_id))


def create_chapter(db: Session, book_id: int, data: ChapterCreate) -> Chapter:
    get_or_raise(db, Book, book_id, book_not_found(book_id))
    chapter = Chapter(book_id=book_id, **data.model_dump())
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


def update_chapter(db: Session, chapter_id: int, data: ChapterUpdate) -> Chapter:
    chapter = get_chapter(db, chapter_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(chapter, field, value)
    db.commit()
    db.refresh(chapter)
    return chapter


def delete_chapter(db: Session, chapter_id: int) -> None:
    chapter = get_chapter(db, chapter_id)
    db.delete(chapter)
    db.commit()