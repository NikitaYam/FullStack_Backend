from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.books import book_not_found
from app.crud.common import get_or_raise
from app.crud.users import user_not_found
from app.models import Book, DiaryLog, User
from app.schemas.diary import DiaryLogCreate, DiaryLogUpdate


def log_not_found(log_id: int) -> str:
    return f"Запись дневника с id={log_id} не найдена"


def list_logs(db: Session, user_id: int, book_id: int | None) -> list[DiaryLog]:
    get_or_raise(db, User, user_id, user_not_found(user_id))
    stmt = select(DiaryLog).where(DiaryLog.user_id == user_id)
    if book_id is not None:
        stmt = stmt.where(DiaryLog.book_id == book_id)
    stmt = stmt.order_by(DiaryLog.date.desc(), DiaryLog.id.desc())
    return list(db.scalars(stmt))


def create_log(db: Session, user_id: int, data: DiaryLogCreate) -> DiaryLog:
    get_or_raise(db, User, user_id, user_not_found(user_id))
    get_or_raise(db, Book, data.book_id, book_not_found(data.book_id))
    # exclude_none: если дата не передана, её проставит БД (DEFAULT CURRENT_DATE)
    log = DiaryLog(user_id=user_id, **data.model_dump(exclude_none=True))
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_log(db: Session, log_id: int, data: DiaryLogUpdate) -> DiaryLog:
    log = get_or_raise(db, DiaryLog, log_id, log_not_found(log_id))
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


def delete_log(db: Session, log_id: int) -> None:
    log = get_or_raise(db, DiaryLog, log_id, log_not_found(log_id))
    db.delete(log)
    db.commit()