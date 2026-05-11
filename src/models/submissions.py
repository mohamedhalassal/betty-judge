from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

def utc_now(): return datetime.now(timezone.utc)

class Submission(SQLModel, table=True):
    id:int |None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    problem_id: int = Field(foreign_key="problem.id")
    source_code: str
    submitted_at: datetime = Field(default_factory=utc_now)
    excution_time: int | None = None
    execution_memory: int | None = None 
    status: str | None = None