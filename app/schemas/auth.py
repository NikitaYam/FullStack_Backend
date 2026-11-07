from typing import Annotated

from pydantic import AfterValidator, EmailStr, StringConstraints

from app.schemas.common import Schema
from app.schemas.user import UserRead

PASSWORD_MAX_LENGTH = 128

# Пробелы в пароле значимы, поэтому общее правило Schema (str_strip_whitespace) здесь отключено.
# Верхняя граница не даёт нагружать сервер хешированием огромных строк.
Password = Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, max_length=PASSWORD_MAX_LENGTH)]
Email = Annotated[EmailStr, AfterValidator(str.lower)]


def strong_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Пароль должен быть не короче 8 символов")
    if not (any(c.isalpha() for c in value) and any(c.isdigit() for c in value)):
        raise ValueError("Пароль должен содержать буквы и цифры")
    return value


class RegisterRequest(Schema):
    name: Annotated[str, StringConstraints(min_length=2, max_length=30)]
    email: Email
    password: Annotated[Password, AfterValidator(strong_password)]


class LoginRequest(Schema):
    # При входе правила сложности не проверяются: они не должны подсказывать, каким пароль быть не может
    email: Email
    password: Password


class UserMe(UserRead):
    """Профиль текущего пользователя: в отличие от публичного UserRead, содержит email."""

    email: str
    is_admin: bool


class AuthResponse(Schema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserMe


class TokenResponse(Schema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
