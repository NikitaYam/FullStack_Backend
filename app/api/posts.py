from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import Limit, Offset, SessionDep
from app.crud import posts as crud
from app.schemas.social import (
    CommentCreate,
    CommentRead,
    PostCreate,
    PostDetail,
    PostRead,
    PostUpdate,
)

router = APIRouter(tags=["Посты"])


@router.get("/posts")
def list_posts(
    db: SessionDep,
    author_id: Annotated[int | None, Query(alias="authorId", gt=0)] = None,
    book_id: Annotated[int | None, Query(alias="bookId", gt=0)] = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[PostRead]:
    return crud.list_posts(db, author_id, book_id, limit, offset)


@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(db: SessionDep, data: PostCreate) -> PostRead:
    return crud.create_post(db, data)


@router.get("/posts/{post_id}")
def get_post(db: SessionDep, post_id: int) -> PostDetail:
    return crud.get_post(db, post_id)


@router.patch("/posts/{post_id}")
def update_post(db: SessionDep, post_id: int, data: PostUpdate) -> PostRead:
    return crud.update_post(db, post_id, data)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(db: SessionDep, post_id: int) -> None:
    crud.delete_post(db, post_id)


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(db: SessionDep, post_id: int, data: CommentCreate) -> CommentRead:
    return crud.add_comment(db, post_id, data)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(db: SessionDep, comment_id: int) -> None:
    crud.delete_comment(db, comment_id)


@router.put("/posts/{post_id}/likes/{user_id}")
def like_post(db: SessionDep, post_id: int, user_id: int) -> PostRead:
    return crud.like_post(db, post_id, user_id)


@router.delete("/posts/{post_id}/likes/{user_id}")
def unlike_post(db: SessionDep, post_id: int, user_id: int) -> PostRead:
    return crud.unlike_post(db, post_id, user_id)