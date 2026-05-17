from sqlmodel import Field, Session, SQLModel
class TestCase(SQLModel, table=True):
    __tablename__ = "test_cases"
    id: int | None = Field(default=None, primary_key=True)
    problem_id: int = Field(foreign_key="problems.id")
    input_data: str
    expected_output: str
    is_sample: bool =  Field(default=False)