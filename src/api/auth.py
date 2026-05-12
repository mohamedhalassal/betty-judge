from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from src.database import engine,get_session, SessionDep
from src.models.user import User
from typing import Annotated

from src.schemas.user import UserResponse

from src.schemas.auth import GoogleLoginRequest

from src.core.google_auth import verify_google_token
from src.core.security import create_access_token

router = APIRouter()

@router.post("/login")
def login(username: str, data: GoogleLoginRequest, session: SessionDep):
    userInfo = verify_google_token(data.token)
    if not userInfo:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    existing_google_id = session.exec(
        select(User).where(User.google_id == userInfo["google_id"])
    ).first()

    if existing_google_id:
        access_token = create_access_token(existing_google_id.id)
        return {"access_token": access_token, "token_type": "bearer"}

    user_db = User(username=username, email=userInfo["email"], google_id=userInfo["google_id"])
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    access_token = create_access_token(user_db.id)
    return {"access_token": access_token, "token_type": "bearer"}

