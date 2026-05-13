from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from .config import  EnvConfig, default_config

ALGORITHM = "HS256"


def create_access_token(user_id: int, td: timedelta | None = None , config: EnvConfig = default_config):
    if td is None:
        td = timedelta(days=7)
    expire = datetime.now(timezone.utc) + td
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, config.client_secret, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str,config: EnvConfig = default_config):
    try:
        payload = jwt.decode(token, config.client_secret, algorithms=[ALGORITHM])
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
if __name__ == "__main__":
    # test
    token = create_access_token(user_id=123, config=EnvConfig(client_secret="your_secret_here"))
    print("Generated Token:", token)
    user_id = verify_access_token(token, config=EnvConfig(client_secret="your_secret_here"))
    print("Verified User ID:", user_id) 
    