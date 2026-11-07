from datetime import datetime

from sqlalchemy import String, Text, false, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=false())
    bio: Mapped[str] = mapped_column(Text, default="")
    favorite_genres: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=list)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())