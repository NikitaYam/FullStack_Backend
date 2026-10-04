from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.crud import diary as crud
from app.schemas.diary import DiaryLogCreate, DiaryLogRead, DiaryLogUpdate

router = APIRouter(tags=["Дневник"])


@router.get("/users/{user_id}/diary")
def list_logs(
    db: SessionDep,
    user_id: int,
    book_id: Annotated[int | None, Query(alias="bookId", gt=0)] = None,
) -> list[DiaryLogRead]:
    return crud.list_logs(db, user_id, book_id)


@router.post("/users/{user_id}/diary", status_code=status.HTTP_201_CREATED)
def create_log(db: SessionDep, user_id: int, data: DiaryLogCreate) -> DiaryLogRead:
    return crud.create_log(db, user_id, data)


@router.patch("/diary/{log_id}")
def update_log(db: SessionDep, log_id: int, data: DiaryLogUpdate) -> DiaryLogRead:
    return crud.update_log(db, log_id, data)


@router.delete("/diary/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(db: SessionDep, log_id: int) -> None:
    crud.delete_log(db, log_id)