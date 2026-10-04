from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.crud import reviews as crud
from app.schemas.book import ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(tags=["Рецензии"])


@router.get("/books/{book_id}/reviews")
def list_book_reviews(db: SessionDep, book_id: int) -> list[ReviewRead]:
    return crud.list_book_reviews(db, book_id)


@router.post("/books/{book_id}/reviews", status_code=status.HTTP_201_CREATED)
def create_review(db: SessionDep, book_id: int, data: ReviewCreate) -> ReviewRead:
    return crud.create_review(db, book_id, data)


@router.get("/users/{user_id}/reviews")
def list_user_reviews(db: SessionDep, user_id: int) -> list[ReviewRead]:
    return crud.list_user_reviews(db, user_id)


@router.patch("/reviews/{review_id}")
def update_review(db: SessionDep, review_id: int, data: ReviewUpdate) -> ReviewRead:
    return crud.update_review(db, review_id, data)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(db: SessionDep, review_id: int) -> None:
    crud.delete_review(db, review_id)