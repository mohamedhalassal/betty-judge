from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserResponse(UserBase):
    id: int
    username: str
    created_at: datetime
