from datetime import datetime

from app.schemas.common import Content, Schema
from app.schemas.user import UserBrief


class MessageCreate(Schema):
    text: Content


class MessageRead(Schema):
    id: int
    sender_id: int
    receiver_id: int
    text: str
    created_at: datetime


class DialogRead(Schema):
    """Элемент списка чатов: собеседник и последнее сообщение."""

    companion: UserBrief
    last_message: MessageRead