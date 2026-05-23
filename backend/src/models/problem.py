from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

def utc_now(): return datetime.now(timezone.utc)
class Problem(SQLModel, table=True):
    __tablename__ = "problems"
    id:int | None = Field(default=None, primary_key=True)
    name: str
    statement: str
    created_at: datetime = Field(default_factory=utc_now)
    created_by: int = Field(foreign_key="users.id")
    solution: str | None = None
    checker_code: str | None = None
    time_limit: int # in ms
    memory_limit: int # in MB
