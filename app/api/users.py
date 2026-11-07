from fastapi import APIRouter, status

from app.api.deps import Limit, Offset, SelfUser, SessionDep
from app.crud import users as crud
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("")
def list_users(db: SessionDep, limit: Limit = 50, offset: Offset = 0) -> list[UserRead]:
    return crud.list_users(db, limit, offset)


@router.get("/{user_id}")
def get_user(db: SessionDep, user_id: int) -> UserRead:
    return crud.get_user(db, user_id)


@router.patch("/{user_id}")
def update_user(db: SessionDep, user_id: int, data: UserUpdate, _: SelfUser) -> UserRead:
    return crud.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: SessionDep, user_id: int, _: SelfUser) -> None:
    crud.delete_user(db, user_id)