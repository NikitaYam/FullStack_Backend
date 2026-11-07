from datetime import datetime

from app.schemas.book import BookBrief
from app.schemas.common import Content, Id, Schema, UpdateSchema
from app.schemas.user import UserBrief


class PostCreate(Schema):
    book_id: Id | None = None
    text: Content


class PostUpdate(UpdateSchema):
    nullable_fields = frozenset({"book_id"})

    book_id: Id | None = None
    text: Content | None = None


class PostRead(Schema):
    id: int
    author_id: int
    author: UserBrief
    book_id: int | None
    book: BookBrief | None
    text: str
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    # Лайкнул ли пост пользователь, сделавший запрос (для анонима всегда False)
    liked_by_me: bool = False


class CommentCreate(Schema):
    text: Content


class CommentRead(Schema):
    id: int
    post_id: int
    author_id: int
    author: UserBrief
    text: str
    created_at: datetime


class PostDetail(PostRead):
    """Пост вместе с комментариями — для страницы поста."""

    comments: list[CommentRead] = []