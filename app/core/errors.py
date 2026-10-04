from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from psycopg import errors as pg_errors
from sqlalchemy.exc import IntegrityError


class AppError(Exception):
    """Ошибка бизнес-логики, которую нужно показать клиенту."""

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT


# Понятные сообщения для ограничений БД (имена заданы NAMING_CONVENTION в app/db/base.py)
CONSTRAINT_MESSAGES = {
    "uq_chapters_book_id_number": "В книге уже есть глава с таким номером",
    "uq_reviews_book_id_author_id": "Пользователь уже оставил рецензию на эту книгу",
    "uq_user_books_user_id_book_id": "Эта книга уже есть на полке",
}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Страховка: нарушение ограничения БД превращается в 409/404/422 вместо 500."""
    orig = exc.orig
    constraint = getattr(getattr(orig, "diag", None), "constraint_name", None)
    message = CONSTRAINT_MESSAGES.get(constraint, f"Нарушено ограничение БД: {constraint}")

    if isinstance(orig, pg_errors.UniqueViolation):
        code = status.HTTP_409_CONFLICT
    elif isinstance(orig, pg_errors.ForeignKeyViolation):
        code = status.HTTP_404_NOT_FOUND
        message = CONSTRAINT_MESSAGES.get(constraint, "Связанная запись не найдена")
    else:
        code = status.HTTP_422_UNPROCESSABLE_CONTENT
    return JSONResponse(status_code=code, content={"detail": message})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)