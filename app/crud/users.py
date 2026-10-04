from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.crud.common import get_or_raise
from app.models import ReadingStatus, User, UserBook
from app.schemas.user import UserCreate, UserRead, UserUpdate


def user_not_found(user_id: int) -> str:
    return f"Пользователь с id={user_id} не найден"


def _select_with_stats() -> Select:
    """Пользователь + количество прочитанных книг (статус done на полке)."""
    books_read = (
        select(func.count(UserBook.id))
        .where(UserBook.user_id == User.id, UserBook.status == ReadingStatus.done)
        .scalar_subquery()
    )
    return select(User, books_read)


def _to_read(user: User, books_read: int) -> UserRead:
    return UserRead.model_validate(user).model_copy(update={"books_read": books_read})


def list_users(db: Session, limit: int, offset: int) -> list[UserRead]:
    stmt = _select_with_stats().order_by(User.id).limit(limit).offset(offset)
    return [_to_read(user, count) for user, count in db.execute(stmt)]


def get_user(db: Session, user_id: int) -> UserRead:
    row = db.execute(_select_with_stats().where(User.id == user_id)).first()
    if row is None:
        raise NotFoundError(user_not_found(user_id))
    return _to_read(*row)


def create_user(db: Session, data: UserCreate) -> UserRead:
    user = User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_read(user, 0)


def update_user(db: Session, user_id: int, data: UserUpdate) -> UserRead:
    user = get_or_raise(db, User, user_id, user_not_found(user_id))
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    return get_user(db, user_id)


def delete_user(db: Session, user_id: int) -> None:
    user = get_or_raise(db, User, user_id, user_not_found(user_id))
    db.delete(user)
    db.commit()