from sqlalchemy import and_, case, or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.crud.common import get_or_raise
from app.crud.users import user_not_found
from app.models import Message, User
from app.schemas.chat import DialogRead, MessageCreate, MessageRead
from app.schemas.user import UserBrief


def _between(user_id: int, other_id: int):
    """Условие «сообщение из переписки этих двух пользователей» (в любую сторону)."""
    return or_(
        and_(Message.sender_id == user_id, Message.receiver_id == other_id),
        and_(Message.sender_id == other_id, Message.receiver_id == user_id),
    )


def list_dialogs(db: Session, user_id: int) -> list[DialogRead]:
    """Список чатов: по одному последнему сообщению с каждым собеседником, свежие сверху."""
    get_or_raise(db, User, user_id, user_not_found(user_id))
    companion_id = case((Message.sender_id == user_id, Message.receiver_id), else_=Message.sender_id)
    # DISTINCT ON (PostgreSQL): из каждой группы «собеседник» берётся первая строка
    # в порядке сортировки, то есть самое новое сообщение
    stmt = (
        select(Message, companion_id)
        .where(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
        .distinct(companion_id)
        .order_by(companion_id, Message.created_at.desc(), Message.id.desc())
    )
    rows = db.execute(stmt).all()

    companions = {u.id: u for u in db.scalars(select(User).where(User.id.in_([r[1] for r in rows])))}
    dialogs = [
        DialogRead(
            companion=UserBrief.model_validate(companions[other]),
            last_message=MessageRead.model_validate(message),
        )
        for message, other in rows
    ]
    dialogs.sort(key=lambda d: (d.last_message.created_at, d.last_message.id), reverse=True)
    return dialogs


def list_messages(
    db: Session, user_id: int, other_id: int, limit: int, offset: int
) -> list[Message]:
    get_or_raise(db, User, user_id, user_not_found(user_id))
    get_or_raise(db, User, other_id, user_not_found(other_id))
    stmt = (
        select(Message)
        .where(_between(user_id, other_id))
        .order_by(Message.created_at, Message.id)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))


def send_message(db: Session, sender_id: int, receiver_id: int, data: MessageCreate) -> Message:
    if sender_id == receiver_id:
        raise AppError("Нельзя отправить сообщение самому себе")
    get_or_raise(db, User, sender_id, user_not_found(sender_id))
    get_or_raise(db, User, receiver_id, user_not_found(receiver_id))
    message = Message(sender_id=sender_id, receiver_id=receiver_id, text=data.text)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message