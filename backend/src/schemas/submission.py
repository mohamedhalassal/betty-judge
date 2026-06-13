from pydantic import BaseModel
from datetime import datetime

from src.models.submission import SubmissionStatus


class SubmissionCreate(BaseModel):
    problem_id: int
    source_code: str


class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    source_code: str
    problem_id: int
    verdict: SubmissionStatus | None
    execution_time: int | None
    execution_memory: int | None
    submitted_at: datetime
