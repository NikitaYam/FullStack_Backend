from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.crud import chapters as crud
from app.schemas.book import ChapterBrief, ChapterCreate, ChapterRead, ChapterUpdate

router = APIRouter(tags=["Главы"])


@router.get("/books/{book_id}/chapters")
def list_chapters(db: SessionDep, book_id: int) -> list[ChapterBrief]:
    return crud.list_chapters(db, book_id)


@router.post("/books/{book_id}/chapters", status_code=status.HTTP_201_CREATED)
def create_chapter(db: SessionDep, book_id: int, data: ChapterCreate) -> ChapterRead:
    return crud.create_chapter(db, book_id, data)


@router.get("/chapters/{chapter_id}")
def get_chapter(db: SessionDep, chapter_id: int) -> ChapterRead:
    return crud.get_chapter(db, chapter_id)


@router.patch("/chapters/{chapter_id}")
def update_chapter(db: SessionDep, chapter_id: int, data: ChapterUpdate) -> ChapterRead:
    return crud.update_chapter(db, chapter_id, data)


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(db: SessionDep, chapter_id: int) -> None:
    crud.delete_chapter(db, chapter_id)