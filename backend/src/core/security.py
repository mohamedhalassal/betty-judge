from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import select

from src.database import SessionDep
from src.models.user import User
from .config import EnvConfig, default_config

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(user_id: int, td: timedelta | None = None , config: EnvConfig = default_config):
    if td is None:
        td = timedelta(days=7)
    expire = datetime.now(timezone.utc) + td
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, config.client_secret, algorithm=ALGORITHM)
    return token


def verify_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> int | None:
    try:
        payload = jwt.decode(token, default_config.client_secret, algorithms=[ALGORITHM])
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
    user_id = verify_access_token(token)
    print("Verified User ID:", user_id)
