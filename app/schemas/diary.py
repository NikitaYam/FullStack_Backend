import datetime as dt
from typing import Annotated

from pydantic import AfterValidator, Field

from app.models.diary import ReadingStatus
from app.schemas.book import BookBrief
from app.schemas.common import Content, Id, OptionalContent, Rating, Schema, UpdateSchema

Progress = Annotated[int, Field(ge=0, le=100)]


def not_in_future(value: dt.date) -> dt.date:
    if value > dt.date.today():
        raise ValueError("Дата записи не может быть в будущем")
    return value


PastDate = Annotated[dt.date, AfterValidator(not_in_future)]


# --- Полка: книга в дневнике пользователя ---


class QuoteCreate(Schema):
    text: Content


class QuoteRead(Schema):
    id: int
    text: str


class ShelfEntryCreate(Schema):
    book_id: Id
    status: ReadingStatus = ReadingStatus.want
    progress: Progress = 0
    rating: Rating | None = None
    notes: OptionalContent = ""


class ShelfEntryUpdate(UpdateSchema):
    nullable_fields = frozenset({"rating"})

    status: ReadingStatus | None = None
    progress: Progress | None = None
    rating: Rating | None = None
    notes: OptionalContent | None = None


class ShelfEntryRead(Schema):
    id: int
    book_id: int
    status: ReadingStatus
    progress: int
    rating: int | None
    notes: str
    added_at: dt.datetime
    book: BookBrief
    quotes: list[QuoteRead]


# --- Дневник чтения: записи по дням ---


class DiaryLogCreate(Schema):
    book_id: Id
    date: PastDate | None = None
    text: Content


class DiaryLogUpdate(UpdateSchema):
    date: PastDate | None = None
    text: Content | None = None


class DiaryLogRead(Schema):
    id: int
    user_id: int
    book_id: int
    date: dt.date
    text: str