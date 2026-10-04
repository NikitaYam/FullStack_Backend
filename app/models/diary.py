import datetime as dt
import enum

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.book import Book


class ReadingStatus(enum.StrEnum):
    want = "want"
    reading = "reading"
    done = "done"


class UserBook(Base):
    """Книга на полке пользователя: статус чтения, прогресс, личная оценка и заметки."""

    __tablename__ = "user_books"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id"),
        CheckConstraint("progress BETWEEN 0 AND 100", name="progress_range"),
        CheckConstraint("rating IS NULL OR rating BETWEEN 1 AND 5", name="rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    status: Mapped[ReadingStatus] = mapped_column(
        Enum(ReadingStatus, name="reading_status"), default=ReadingStatus.want
    )
    progress: Mapped[int] = mapped_column(default=0)
    rating: Mapped[int | None]
    notes: Mapped[str] = mapped_column(Text, default="")
    added_at: Mapped[dt.datetime] = mapped_column(server_default=func.now())

    book: Mapped[Book] = relationship()
    quotes: Mapped[list["Quote"]] = relationship(
        back_populates="user_book",
        order_by="Quote.id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_book_id: Mapped[int] = mapped_column(ForeignKey("user_books.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)

    user_book: Mapped[UserBook] = relationship(back_populates="quotes")


class DiaryLog(Base):
    """Запись в дневнике чтения за конкретный день."""

    __tablename__ = "diary_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    date: Mapped[dt.date] = mapped_column(server_default=func.current_date())
    text: Mapped[str] = mapped_column(Text)