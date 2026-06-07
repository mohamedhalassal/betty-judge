from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from src.database import engine, get_session, SessionDep
from src.models.user import User
from typing import Annotated, Callable

from src.schemas.user import UserResponse,UpdateUsernameRequest

from src.schemas.auth import GoogleLoginRequest

from src.core.google_auth import verify_google_token
from src.core.security import create_access_token, get_current_user
from src.core.username import generate_unique_username

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
):
    userInfo = verify_token(data.token)
    if not userInfo:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    existing_user = session.exec(
        select(User).where(User.google_id == userInfo["google_id"])
    ).first()

    if existing_user and existing_user.id:
        access_token = create_access_token(existing_user.id)
        # TODO: add it in Client Cookies
        return {"access_token": access_token, "token_type": "bearer"}
    
    generated_username = generate_unique_username(userInfo["email"], session)

    user_db = User(
        username=generated_username, email=userInfo["email"], google_id=userInfo["google_id"]
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    access_token = create_access_token(user_db.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.patch("/me/username", response_model=UserResponse)
def update_username(
    data: UpdateUsernameRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    existing_user = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=400, detail="Username already taken")

    current_user.username = data.username
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user