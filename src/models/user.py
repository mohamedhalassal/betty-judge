from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

def utc_now(): return datetime.now(timezone.utc)
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    google_id: str = Field(unique=True)
    email: str
    username: str = Field(unique=True, max_length=16)
    created_at: datetime = Field(default_factory=utc_now)
