from datetime import datetime
from typing import Annotated

from pydantic import Field

from app.schemas.common import OptionalContent, Schema, UpdateSchema

UserName = Annotated[str, Field(min_length=1, max_length=100)]
Genres = Annotated[list[Annotated[str, Field(min_length=1, max_length=50)]], Field(max_length=20)]


class UserBase(Schema):
    name: UserName
    bio: OptionalContent = ""
    favorite_genres: Genres = []


class UserCreate(UserBase):
    pass


class UserUpdate(UpdateSchema):
    name: UserName | None = None
    bio: OptionalContent | None = None
    favorite_genres: Genres | None = None


class UserBrief(Schema):
    id: int
    name: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    books_read: int = 0