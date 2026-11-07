from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.db.base import Base

from app.models import User


def get_or_raise[M: Base](db: Session, model: type[M], obj_id: int, message: str) -> M:
    """Возвращает запись по первичному ключу или выбрасывает NotFoundError (404)."""
    obj = db.get(model, obj_id)
    if obj is None:
        raise NotFoundError(message)
    return obj


def require_owner(owner_id: int, user_id: int) -> None:
    """Проверка права на операцию: менять запись может только её владелец."""
    if owner_id != user_id:
        raise ForbiddenError("Можно изменять только свои записи")

def require_owner_or_admin(owner_id: int, user: User) -> None:
    """Удалить чужую запись может только администратор"""
    if owner_id != user.id and not user.is_admin:
        raise ForbiddenError("Можно изменять только свои записи")