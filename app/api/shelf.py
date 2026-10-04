from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.crud import shelf as crud
from app.models import ReadingStatus
from app.schemas.diary import QuoteCreate, QuoteRead, ShelfEntryCreate, ShelfEntryRead, ShelfEntryUpdate

router = APIRouter(tags=["Полка"])


@router.get("/users/{user_id}/shelf")
def list_shelf(
    db: SessionDep,
    user_id: int,
    status_filter: Annotated[ReadingStatus | None, Query(alias="status")] = None,
) -> list[ShelfEntryRead]:
    return crud.list_shelf(db, user_id, status_filter)


@router.post("/users/{user_id}/shelf", status_code=status.HTTP_201_CREATED)
def add_to_shelf(db: SessionDep, user_id: int, data: ShelfEntryCreate) -> ShelfEntryRead:
    return crud.add_to_shelf(db, user_id, data)


@router.get("/users/{user_id}/shelf/{book_id}")
def get_entry(db: SessionDep, user_id: int, book_id: int) -> ShelfEntryRead:
    return crud.get_entry(db, user_id, book_id)


@router.patch("/users/{user_id}/shelf/{book_id}")
def update_entry(
    db: SessionDep, user_id: int, book_id: int, data: ShelfEntryUpdate
) -> ShelfEntryRead:
    return crud.update_entry(db, user_id, book_id, data)


@router.delete("/users/{user_id}/shelf/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_shelf(db: SessionDep, user_id: int, book_id: int) -> None:
    crud.remove_from_shelf(db, user_id, book_id)


@router.post("/users/{user_id}/shelf/{book_id}/quotes", status_code=status.HTTP_201_CREATED)
def add_quote(db: SessionDep, user_id: int, book_id: int, data: QuoteCreate) -> QuoteRead:
    return crud.add_quote(db, user_id, book_id, data)


@router.delete("/quotes/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(db: SessionDep, quote_id: int) -> None:
    crud.delete_quote(db, quote_id)