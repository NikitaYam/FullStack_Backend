from fastapi import APIRouter, status

from app.api.deps import Limit, Offset, SessionDep
from app.crud import chats as crud
from app.schemas.chat import DialogRead, MessageCreate, MessageRead

router = APIRouter(prefix="/users/{user_id}/chats", tags=["Чаты"])


@router.get("")
def list_dialogs(db: SessionDep, user_id: int) -> list[DialogRead]:
    return crud.list_dialogs(db, user_id)


@router.get("/{other_id}/messages")
def list_messages(
    db: SessionDep, user_id: int, other_id: int, limit: Limit = 100, offset: Offset = 0
) -> list[MessageRead]:
    return crud.list_messages(db, user_id, other_id, limit, offset)


@router.post("/{other_id}/messages", status_code=status.HTTP_201_CREATED)
def send_message(db: SessionDep, user_id: int, other_id: int, data: MessageCreate) -> MessageRead:
    return crud.send_message(db, user_id, other_id, data)