from sqlmodel import Field, SQLModel

class Submission(SQLModel, table=True):
    __tablename__ = "submissions"

    id: int | None = Field(default=None, primary_key=True)
    problem_id: int
    source_code: str
    status: str | None = None