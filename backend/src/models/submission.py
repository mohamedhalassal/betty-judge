from datetime import datetime, timezone
from pydantic import BaseModel
from enum import Enum
from sqlmodel import Field, Session, SQLModel, create_engine, select

def utc_now(): return datetime.now(timezone.utc)

class SubmissionStatus(str, Enum):
    IN_QUEUE = "in queue"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong answer"
    TIME_LIMIT_EXCEEDED = "time limit exceeded"
    RUNTIME_ERROR = "runtime error"
    COMPILE_ERROR = "compile error"
    MEMORY_LIMIT_EXCEEDED = "memory limit exceeded"
    IDLENESS_LIMIT_EXCEEDED = "idleness limit exceeded"
    FAILED = "failed"

class Submission(SQLModel, table=True):
    __tablename__ = "submissions"
    id:int |None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    problem_id: int = Field(foreign_key="problems.id")
    source_code: str
    submitted_at: datetime = Field(default_factory=utc_now)
    execution_time: int | None = None
    execution_memory: int | None = None 
    verdict : SubmissionStatus = Field(default=SubmissionStatus.IN_QUEUE)
