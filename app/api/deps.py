from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User

SessionDep = Annotated[Session, Depends(get_db)]

Limit = Annotated[int, Query(ge=1, le=100, description="Сколько записей вернуть")]
Offset = Annotated[int, Query(ge=0, description="Сколько записей пропустить")]

_bearer = HTTPBearer(auto_error=False, description="Access token из /api/auth/login")


def get_optional_user(
    db: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User | None:
    """Для публичных маршрутов, где вошедший пользователь видит чуть больше (например, свои лайки)."""
    user_id = decode_access_token(credentials.credentials) if credentials else None
    return db.get(User, user_id) if user_id is not None else None


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


def get_current_user(user: OptionalUser) -> User:
    """Аутентификация: кто делает запрос. Нет или неверный токен — 401."""
    if user is None:
        raise UnauthorizedError("Требуется вход в систему")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_self(user_id: int, current_user: CurrentUser) -> User:
    """Авторизация для маршрутов /users/{user_id}/...: личные данные доступны только их владельцу."""
    if current_user.id != user_id:
        raise ForbiddenError("Нет доступа к данным другого пользователя")
    return current_user


SelfUser = Annotated[User, Depends(require_self)]


def require_admin(current_user: CurrentUser) -> User:
    """Каталог книг общий для всех, поэтому менять его может только администратор."""
    if not current_user.is_admin:
        raise ForbiddenError("Действие доступно только администратору")
    return current_user


AdminUser = Annotated[User, Depends(require_admin)]
