from fastapi import APIRouter, status

from app.api.deps import Limit, Offset, SessionDep
from app.crud import users as crud
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("")
def list_users(db: SessionDep, limit: Limit = 50, offset: Offset = 0) -> list[UserRead]:
    return crud.list_users(db, limit, offset)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(db: SessionDep, data: UserCreate) -> UserRead:
    return crud.create_user(db, data)


@router.get("/{user_id}")
def get_user(db: SessionDep, user_id: int) -> UserRead:
    return crud.get_user(db, user_id)


@router.patch("/{user_id}")
def update_user(db: SessionDep, user_id: int, data: UserUpdate) -> UserRead:
    return crud.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: SessionDep, user_id: int) -> None:
    crud.delete_user(db, user_id)