from typing import Annotated

from fastapi import APIRouter, Cookie, Response, status

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.security import create_access_token
from app.crud import auth as crud
from app.crud.users import get_user
from app.models import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, TokenResponse, UserMe

router = APIRouter(prefix="/auth", tags=["Авторизация"])

REFRESH_COOKIE = "refresh_token"
# Cookie уходит только на маршруты авторизации, а не с каждым запросом к API
REFRESH_COOKIE_PATH = "/api/auth"

RefreshCookie = Annotated[str | None, Cookie(alias=REFRESH_COOKIE)]


def _set_refresh_cookie(response: Response, token: str) -> None:
    """httponly: токен недоступен из JavaScript, поэтому его не украсть через XSS.
    samesite=lax: браузер не отправит cookie с POST-запросом с чужого сайта (защита от CSRF).
    """
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


def _expires_in() -> int:
    return settings.access_token_expire_minutes * 60


def _auth_response(db: SessionDep, user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user.id),
        expires_in=_expires_in(),
        user=_user_me(db, user),
    )


def _user_me(db: SessionDep, user: User) -> UserMe:
    return UserMe(
        **get_user(db, user.id).model_dump(),
        email=user.email,
        is_admin=user.is_admin,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(db: SessionDep, data: RegisterRequest, response: Response) -> AuthResponse:
    user, refresh_token = crud.register(db, data)
    _set_refresh_cookie(response, refresh_token)
    return _auth_response(db, user)


@router.post("/login")
def login(db: SessionDep, data: LoginRequest, response: Response) -> AuthResponse:
    user, refresh_token = crud.login(db, data)
    _set_refresh_cookie(response, refresh_token)
    return _auth_response(db, user)


@router.post("/refresh")
def refresh(db: SessionDep, refresh_token: RefreshCookie = None) -> TokenResponse:
    user = crud.get_user_by_refresh_token(db, refresh_token)
    return TokenResponse(access_token=create_access_token(user.id), expires_in=_expires_in())


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(db: SessionDep, response: Response, refresh_token: RefreshCookie = None) -> None:
    """Не требует access token: выйти должно быть можно и после его истечения."""
    crud.revoke_refresh_token(db, refresh_token)
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH)


@router.get("/me")
def me(db: SessionDep, current_user: CurrentUser) -> UserMe:
    return _user_me(db, current_user)
