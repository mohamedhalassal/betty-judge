from pydantic import BaseModel
from datetime import datetime


class ProblemCreate(BaseModel):
    name: str
    statement: str
    solution: str | None = None
    checker_code: str | None = None
    time_limit: int
    memory_limit: int



class ProblemResponse(BaseModel):
    id: int
    name: str
    statement: str
    created_at: datetime