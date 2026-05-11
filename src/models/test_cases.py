from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

def utc_now(): return datetime.now(timezone.utc)

class TestCases(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    problem_id: int = Field(foreign_key="problem.id")
    input_data: str
    expected_output: str
    is_sample: bool =  Field(default=False)