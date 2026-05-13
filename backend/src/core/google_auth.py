from google.oauth2 import id_token
from google.auth.transport import requests
from .config import CLIENT_ID


def verify_google_token(token: str):
    try:
        user_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        return {
            "google_id": user_info.get("sub"),
            "email": user_info.get("email"),
        }
    except Exception:
        return None

