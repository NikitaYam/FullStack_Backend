from datetime import datetime

from app.schemas.common import Content, Id, Schema, UpdateSchema


class PostCreate(Schema):
    author_id: Id
    book_id: Id | None = None
    text: Content


class PostUpdate(UpdateSchema):
    nullable_fields = frozenset({"book_id"})

    book_id: Id | None = None
    text: Content | None = None


class PostRead(Schema):
    id: int
    author_id: int
    book_id: int | None
    text: str
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0


class CommentCreate(Schema):
    author_id: Id
    text: Content


class CommentRead(Schema):
    id: int
    post_id: int
    author_id: int
    text: str
    created_at: datetime


class PostDetail(PostRead):
    """Пост вместе с комментариями — для страницы поста."""

    comments: list[CommentRead] = []