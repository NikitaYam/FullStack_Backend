from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.db.base import Base


def get_or_raise[M: Base](db: Session, model: type[M], obj_id: int, message: str) -> M:
    """Возвращает запись по первичному ключу или выбрасывает NotFoundError (404)."""
    obj = db.get(model, obj_id)
    if obj is None:
        raise NotFoundError(message)
    return obj