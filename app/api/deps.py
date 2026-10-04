from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db

SessionDep = Annotated[Session, Depends(get_db)]

Limit = Annotated[int, Query(ge=1, le=100, description="Сколько записей вернуть")]
Offset = Annotated[int, Query(ge=0, description="Сколько записей пропустить")]