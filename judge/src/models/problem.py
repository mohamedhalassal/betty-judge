from sqlmodel import Field, SQLModel


class Problem(SQLModel, table=True):
    __tablename__ = "problems"

    id: int | None = Field(default=None, primary_key=True)