from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    token: str