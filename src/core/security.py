from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from .config import CLIENT_SECRET

ALGORITHM = "HS256"


def create_access_token(user_id: int, td: timedelta | None = None):
    if td is None:
        td = timedelta(days=7)
    expire = datetime.now(timezone.utc) + td
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, CLIENT_SECRET, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, CLIENT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        expr = payload.get("exp")

        if expr is not None and datetime.fromtimestamp(
            expr, tz=timezone.utc
        ) < datetime.now(timezone.utc):
            return None

        return int(user_id)
    except:
        return None
