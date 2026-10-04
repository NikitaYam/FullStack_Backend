from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import Limit, Offset, SessionDep
from app.crud import books as crud
from app.schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["Книги"])


@router.get("")
def list_books(
    db: SessionDep,
    search: Annotated[str | None, Query(max_length=100, description="Поиск по названию и автору")] = None,
    genre: Annotated[str | None, Query(max_length=100)] = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[BookRead]:
    return crud.list_books(db, search, genre, limit, offset)


# Объявлен до /{book_id}, иначе FastAPI попробует разобрать "genres" как book_id и вернёт 422
@router.get("/genres")
def list_genres(db: SessionDep) -> list[str]:
    return crud.list_genres(db)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_book(db: SessionDep, data: BookCreate) -> BookRead:
    return crud.create_book(db, data)


@router.get("/{book_id}")
def get_book(db: SessionDep, book_id: int) -> BookRead:
    return crud.get_book(db, book_id)


@router.patch("/{book_id}")
def update_book(db: SessionDep, book_id: int, data: BookUpdate) -> BookRead:
    return crud.update_book(db, book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(db: SessionDep, book_id: int) -> None:
    crud.delete_book(db, book_id)