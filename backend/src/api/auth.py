from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from src.database import engine, get_session, SessionDep
from src.models.user import User
from typing import Annotated, Callable

from src.schemas.user import UserResponse

from src.schemas.auth import GoogleLoginRequest

from src.core.google_auth import verify_google_token
from src.core.security import create_access_token, get_current_user

router = APIRouter()


def get_google_token_verifier():
    return verify_google_token


GoogleTokenVerifierDep = Annotated[
    Callable[[str], dict | None],
    Depends(get_google_token_verifier),
]


@router.post("/login")
def login(
    data: GoogleLoginRequest,
    session: SessionDep,
    verify_token: GoogleTokenVerifierDep,
    username: str | None = None,
):
    userInfo = verify_token(data.token)
    if not userInfo:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    existing_google_id = session.exec(
        select(User).where(User.google_id == userInfo["google_id"])
    ).first()

    if existing_google_id and existing_google_id.id:
        access_token = create_access_token(existing_google_id.id)
        # TODO: add it in Client Cookies
        return {"access_token": access_token, "token_type": "bearer"}

    if not username:
        raise HTTPException(
            status_code=404,
            detail="User not found. Username required for registration.",
        )

    existing_username = session.exec(
        select(User).where(User.username == username)
    ).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken.")

    user_db = User(
        username=username, email=userInfo["email"], google_id=userInfo["google_id"]
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    access_token = create_access_token(user_db.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
