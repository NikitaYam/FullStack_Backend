from datetime import datetime
from typing import Annotated

from pydantic import Field

from app.schemas.common import Content, Id, OptionalContent, Rating, Schema, Title, UpdateSchema

Genre = Annotated[str, Field(min_length=1, max_length=100)]
Year = Annotated[int, Field(ge=0, le=2100)]
HexColor = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
ChapterNumber = Annotated[int, Field(ge=1)]


# --- Книги ---


class BookBase(Schema):
    title: Title
    author: Title
    genre: Genre
    year: Year | None = None
    description: OptionalContent = ""
    color: HexColor = "#888888"


class BookCreate(BookBase):
    pass


class BookUpdate(UpdateSchema):
    nullable_fields = frozenset({"year"})

    title: Title | None = None
    author: Title | None = None
    genre: Genre | None = None
    year: Year | None = None
    description: OptionalContent | None = None
    color: HexColor | None = None


class BookBrief(Schema):
    id: int
    title: str
    author: str
    genre: str
    color: str


class BookRead(BookBase):
    id: int
    rating: float | None = None
    reviews_count: int = 0


# --- Главы ---


class ChapterBase(Schema):
    number: ChapterNumber
    title: Title
    paragraphs: list[Content] = []


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(UpdateSchema):
    number: ChapterNumber | None = None
    title: Title | None = None
    paragraphs: list[Content] | None = None


class ChapterBrief(Schema):
    """Пункт оглавления — без текста главы."""

    id: int
    number: int
    title: str


class ChapterRead(ChapterBase):
    id: int
    book_id: int


# --- Рецензии ---


class ReviewCreate(Schema):
    author_id: Id
    rating: Rating
    text: OptionalContent = ""


class ReviewUpdate(UpdateSchema):
    rating: Rating | None = None
    text: OptionalContent | None = None


class ReviewRead(Schema):
    id: int
    book_id: int
    author_id: int
    rating: int
    text: str
    created_at: datetime