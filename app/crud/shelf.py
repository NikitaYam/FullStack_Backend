from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.errors import NotFoundError
from app.crud.books import book_not_found
from app.crud.common import get_or_raise
from app.crud.users import user_not_found
from app.models import Book, Quote, ReadingStatus, User, UserBook
from app.schemas.diary import QuoteCreate, ShelfEntryCreate, ShelfEntryUpdate


def entry_not_found(user_id: int, book_id: int) -> str:
    return f"Книги с id={book_id} нет на полке пользователя с id={user_id}"


def quote_not_found(quote_id: int) -> str:
    return f"Цитата с id={quote_id} не найдена"


def _select_entries() -> Select:
    """Запись полки сразу с книгой и цитатами, чтобы не делать по запросу на каждую запись."""
    return select(UserBook).options(joinedload(UserBook.book), selectinload(UserBook.quotes))


def _apply_status_rules(entry: UserBook, changes: dict) -> None:
    """Бизнес-правило: дочитанная книга (done) получает прогресс 100%, если клиент не указал другой."""
    if changes.get("status") == ReadingStatus.done and "progress" not in changes:
        entry.progress = 100


def list_shelf(db: Session, user_id: int, status: ReadingStatus | None) -> list[UserBook]:
    get_or_raise(db, User, user_id, user_not_found(user_id))
    stmt = _select_entries().where(UserBook.user_id == user_id)
    if status is not None:
        stmt = stmt.where(UserBook.status == status)
    stmt = stmt.order_by(UserBook.added_at.desc(), UserBook.id.desc())
    return list(db.scalars(stmt))


def get_entry(db: Session, user_id: int, book_id: int) -> UserBook:
    stmt = _select_entries().where(UserBook.user_id == user_id, UserBook.book_id == book_id)
    entry = db.scalar(stmt)
    if entry is None:
        raise NotFoundError(entry_not_found(user_id, book_id))
    return entry


def add_to_shelf(db: Session, user_id: int, data: ShelfEntryCreate) -> UserBook:
    get_or_raise(db, User, user_id, user_not_found(user_id))
    get_or_raise(db, Book, data.book_id, book_not_found(data.book_id))
    entry = UserBook(user_id=user_id, **data.model_dump())
    _apply_status_rules(entry, data.model_dump(exclude_unset=True))
    db.add(entry)
    db.commit()
    return get_entry(db, user_id, data.book_id)


def update_entry(db: Session, user_id: int, book_id: int, data: ShelfEntryUpdate) -> UserBook:
    entry = get_entry(db, user_id, book_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(entry, field, value)
    _apply_status_rules(entry, changes)
    db.commit()
    db.refresh(entry)
    return entry


def remove_from_shelf(db: Session, user_id: int, book_id: int) -> None:
    entry = get_entry(db, user_id, book_id)
    db.delete(entry)
    db.commit()


def add_quote(db: Session, user_id: int, book_id: int, data: QuoteCreate) -> Quote:
    entry = get_entry(db, user_id, book_id)
    quote = Quote(user_book_id=entry.id, text=data.text)
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def delete_quote(db: Session, quote_id: int) -> None:
    quote = get_or_raise(db, Quote, quote_id, quote_not_found(quote_id))
    db.delete(quote)
    db.commit()