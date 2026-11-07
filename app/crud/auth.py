import datetime as dt

from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_dummy_password,
    verify_password,
)
from app.models import RefreshToken, User
from app.schemas.auth import LoginRequest, RegisterRequest


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _issue_refresh_token(db: Session, user: User) -> str:
    """Создаёт сессию. Заодно убирает истёкшие и отозванные сессии пользователя, чтобы таблица не росла."""
    now = _now()
    db.execute(
        delete(RefreshToken).where(
            RefreshToken.user_id == user.id,
            or_(RefreshToken.expires_at < now, RefreshToken.revoked_at.is_not(None)),
        )
    )
    token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(token),
            expires_at=now + dt.timedelta(days=settings.refresh_token_expire_days),
        )
    )
    db.commit()
    return token


def register(db: Session, data: RegisterRequest) -> tuple[User, str]:
    if db.scalar(select(User.id).where(User.email == data.email)) is not None:
        raise ConflictError("Пользователь с таким email уже зарегистрирован")
    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.flush()
    return user, _issue_refresh_token(db, user)


def login(db: Session, data: LoginRequest) -> tuple[User, str]:
    user = db.scalar(select(User).where(User.email == data.email))
    if user is None:
        verify_dummy_password(data.password)
        raise UnauthorizedError("Неверный email или пароль")
    if not verify_password(data.password, user.password_hash):
        raise UnauthorizedError("Неверный email или пароль")
    return user, _issue_refresh_token(db, user)


def get_user_by_refresh_token(db: Session, token: str | None) -> User:
    """Отказ для всех трёх случаев одинаковый: некорректный, истёкший или отозванный токен."""
    invalid = UnauthorizedError("Сессия истекла, войдите снова")
    if not token:
        raise invalid
    session = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(token)))
    if session is None or session.revoked_at is not None or session.expires_at <= _now():
        raise invalid
    user = db.get(User, session.user_id)
    if user is None:
        raise invalid
    return user


def revoke_refresh_token(db: Session, token: str | None) -> None:
    """Выход идемпотентен: повторный выход или неизвестный токен — не ошибка."""
    if not token:
        return
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(token), RefreshToken.revoked_at.is_(None))
        .values(revoked_at=_now())
    )
    db.commit()
