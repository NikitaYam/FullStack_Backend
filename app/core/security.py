import datetime as dt
import hashlib
import secrets

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError

from app.core.config import settings

JWT_ALGORITHM = "HS256"

# Argon2 — алгоритм, созданный специально для хранения паролей: медленный и требовательный к памяти
_password_hash = PasswordHash.recommended()

# Хеш для проверки, когда пользователь не найден: иначе вход с несуществующим email
# отвечал бы заметно быстрее, и по времени ответа можно было бы подбирать чужие адреса
_dummy_hash = _password_hash.hash(secrets.token_urlsafe(32))


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hash.verify(password, password_hash)
    except PwdlibError:
        # Запись без настоящего хеша (пользователи, созданные до появления паролей)
        return False


def verify_dummy_password(password: str) -> None:
    _password_hash.verify(password, _dummy_hash)


def create_access_token(user_id: int) -> str:
    now = dt.datetime.now(dt.UTC)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + dt.timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Возвращает id пользователя или None, если токен подделан, истёк или имеет другой тип."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"]) if payload.get("type") == "access" else None
    except (jwt.InvalidTokenError, ValueError):
        return None


def generate_refresh_token() -> str:
    """Refresh token — случайная строка, а не JWT: его всё равно нужно проверять по БД."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """В БД лежит только хеш: утечка таблицы не даёт готовых токенов.

    Быстрого SHA-256 достаточно: токен длинный и случайный, перебирать его бессмысленно.
    """
    return hashlib.sha256(token.encode()).hexdigest()
