from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from .config import  EnvConfig, default_config


def verify_google_token(token: str, config: EnvConfig = default_config):
    # Try verifying as an ID Token first
    try:
        user_info = id_token.verify_oauth2_token(token, google_requests.Request(), config.client_id)
        return {
            "google_id": user_info.get("sub"),
            "email": user_info.get("email"),
        }
    except Exception as e:
        print("ID Token verification failed:", e)
        pass
        
    # Fallback to verifying as an Access Token (what useGoogleLogin provides)
    try:
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            data = response.json()
            return {
                "google_id": data.get("sub"),
                "email": data.get("email"),
            }
        else:
            print("Access Token verification failed. Status:", response.status_code, "Body:", response.text)
    except Exception as e:
        print("Access Token request failed:", e)
        pass

    return None

