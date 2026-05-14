from google.oauth2 import id_token
from google.auth.transport import requests
from .config import  EnvConfig, default_config


def verify_google_token(token: str, config: EnvConfig = default_config):
    try:
        user_info = id_token.verify_oauth2_token(token, requests.Request(), default_config.client_id)
        return {
            "google_id": user_info.get("sub"),
            "email": user_info.get("email"),
        }
    except:
        return None

