from pydantic import BaseModel
from datetime import datetime


class SubmissionCreate(BaseModel):
    problem_id: int
    source_code: str


class SubmissionResponse(BaseModel):
    problem_id: int
    verdict: str | None
    execution_time: int | None
    submitted_at: datetime