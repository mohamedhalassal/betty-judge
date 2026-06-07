from pydantic import BaseModel,Field, field_validator
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserResponse(UserBase):
    id: int
    username: str
    created_at: datetime

class UpdateUsernameRequest(BaseModel):
     username: str = Field(
        min_length=3,
        max_length=16,
        pattern=r"^[a-zA-Z0-9_]+$"
    )
     @field_validator("username")
     @classmethod
     def normalize_username(cls, v):
         return v.lower()