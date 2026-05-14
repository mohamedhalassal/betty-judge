from datetime import datetime, timedelta, timezone
from operator import ge
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import select

from src.database import SessionDep
from src.models.user import User
from .config import EnvConfig, get_config   

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/google-login")


def create_access_token(user_id: int, td: timedelta | None = None , config: EnvConfig | None = None) -> str:
    if td is None:
        td = timedelta(days=7)
    if config is None:
        config = get_config()
    expire = datetime.now(timezone.utc) + td
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, config.jwt_secret_key, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str, config: EnvConfig | None = None) -> int | None:
    if config is None:
        config = get_config()
    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        expr = payload.get("exp")

        if expr is not None and datetime.fromtimestamp(
            expr, tz=timezone.utc
        ) < datetime.now(timezone.utc):
            return None

        return int(user_id)
    except (JWTError, ValueError):
        return None


def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> int | None:
    return decode_access_token(token)


def get_current_user(
    user_id: Annotated[int | None, Depends(verify_access_token)],
    session: SessionDep,
) -> User:
    http_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user_id is None:
        raise http_exception

    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise http_exception
    return user


if __name__ == "__main__":
    # test
    token = create_access_token(user_id=123)
    print("Generated Token:", token)
    user_id = decode_access_token(token)
    print("Verified User ID:", user_id)
