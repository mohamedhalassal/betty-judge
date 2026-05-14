from datetime import datetime, timezone
from pydantic import BaseModel
from enum import Enum
from sqlmodel import Field, Session, SQLModel, create_engine, select

def utc_now(): return datetime.now(timezone.utc)

class SubmissionStatus(str, Enum):
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"

class Submission(SQLModel, table=True):
    __tablename__ = "submissions"
    id:int |None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    problem_id: int = Field(foreign_key="problems.id")
    source_code: str
    submitted_at: datetime = Field(default_factory=utc_now)
    execution_time: int | None = None
    execution_memory: int | None = None 
    status: SubmissionStatus | None = Field(default=None)