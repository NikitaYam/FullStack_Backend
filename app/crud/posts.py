from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import NotFoundError
from app.crud.books import book_not_found
from app.crud.common import get_or_raise
from app.crud.users import user_not_found
from app.models import Book, Post, PostComment, PostLike, User
from app.schemas.social import CommentCreate, PostCreate, PostDetail, PostRead, PostUpdate


def post_not_found(post_id: int) -> str:
    return f"Пост с id={post_id} не найден"


def comment_not_found(comment_id: int) -> str:
    return f"Комментарий с id={comment_id} не найден"


def _select_with_stats() -> Select:
    """Пост + количество лайков и комментариев."""
    likes = select(func.count()).where(PostLike.post_id == Post.id).scalar_subquery()
    comments = select(func.count()).where(PostComment.post_id == Post.id).scalar_subquery()
    return select(Post, likes, comments)


def _to_read[S: PostRead](schema: type[S], post: Post, likes: int, comments: int) -> S:
    return schema.model_validate(post).model_copy(
        update={"likes_count": likes, "comments_count": comments}
    )


def list_posts(
    db: Session, author_id: int | None, book_id: int | None, limit: int, offset: int
) -> list[PostRead]:
    stmt = _select_with_stats()
    if author_id is not None:
        stmt = stmt.where(Post.author_id == author_id)
    if book_id is not None:
        stmt = stmt.where(Post.book_id == book_id)
    stmt = stmt.order_by(Post.created_at.desc(), Post.id.desc()).limit(limit).offset(offset)
    return [_to_read(PostRead, *row) for row in db.execute(stmt)]


def get_post(db: Session, post_id: int) -> PostDetail:
    stmt = _select_with_stats().options(selectinload(Post.comments)).where(Post.id == post_id)
    row = db.execute(stmt).first()
    if row is None:
        raise NotFoundError(post_not_found(post_id))
    return _to_read(PostDetail, *row)


def _get_post_read(db: Session, post_id: int) -> PostRead:
    row = db.execute(_select_with_stats().where(Post.id == post_id)).first()
    if row is None:
        raise NotFoundError(post_not_found(post_id))
    return _to_read(PostRead, *row)


def create_post(db: Session, data: PostCreate) -> PostRead:
    get_or_raise(db, User, data.author_id, user_not_found(data.author_id))
    if data.book_id is not None:
        get_or_raise(db, Book, data.book_id, book_not_found(data.book_id))
    post = Post(**data.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return _to_read(PostRead, post, 0, 0)


def update_post(db: Session, post_id: int, data: PostUpdate) -> PostRead:
    post = get_or_raise(db, Post, post_id, post_not_found(post_id))
    changes = data.model_dump(exclude_unset=True)
    if changes.get("book_id") is not None:
        get_or_raise(db, Book, changes["book_id"], book_not_found(changes["book_id"]))
    for field, value in changes.items():
        setattr(post, field, value)
    db.commit()
    return _get_post_read(db, post_id)


def delete_post(db: Session, post_id: int) -> None:
    post = get_or_raise(db, Post, post_id, post_not_found(post_id))
    db.delete(post)
    db.commit()


# --- Комментарии ---


def add_comment(db: Session, post_id: int, data: CommentCreate) -> PostComment:
    get_or_raise(db, Post, post_id, post_not_found(post_id))
    get_or_raise(db, User, data.author_id, user_not_found(data.author_id))
    comment = PostComment(post_id=post_id, **data.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: int) -> None:
    comment = get_or_raise(db, PostComment, comment_id, comment_not_found(comment_id))
    db.delete(comment)
    db.commit()


# --- Лайки ---


def like_post(db: Session, post_id: int, user_id: int) -> PostRead:
    """Идемпотентно: повторный лайк того же пользователя ничего не меняет."""
    get_or_raise(db, Post, post_id, post_not_found(post_id))
    get_or_raise(db, User, user_id, user_not_found(user_id))
    if db.get(PostLike, (post_id, user_id)) is None:
        db.add(PostLike(post_id=post_id, user_id=user_id))
        db.commit()
    return _get_post_read(db, post_id)


def unlike_post(db: Session, post_id: int, user_id: int) -> PostRead:
    """Идемпотентно: снять несуществующий лайк — не ошибка."""
    get_or_raise(db, Post, post_id, post_not_found(post_id))
    like = db.get(PostLike, (post_id, user_id))
    if like is not None:
        db.delete(like)
        db.commit()
    return _get_post_read(db, post_id)