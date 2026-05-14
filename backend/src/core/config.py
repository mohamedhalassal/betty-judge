import os
from pydantic import BaseModel


class EnvConfig(BaseModel):
    is_prod: bool 
    client_id: str 
    jwt_secret_key: str 
    database_url: str 

def get_config() -> EnvConfig:
    ENV = os.getenv("ENV", "development")

    CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    if CLIENT_ID is None or CLIENT_ID == "":
        raise ValueError("GOOGLE_CLIENT_ID environment variable is not set")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    if JWT_SECRET_KEY is None or JWT_SECRET_KEY == "":
        raise ValueError("JWT_SECRET_KEY environment variable is not set")

    DATABASE_URL = os.environ.get("DATABASE_URL")
    if ENV == "development" and (DATABASE_URL is None or DATABASE_URL == ""):
        DATABASE_URL = "sqlite://./database.db"

    if DATABASE_URL is None or DATABASE_URL == "":
        raise ValueError("DATABASE_URL environment variable is not set")

    return EnvConfig(
        is_prod=ENV == "production",
        client_id=CLIENT_ID,
        jwt_secret_key=JWT_SECRET_KEY,
        database_url=DATABASE_URL
    )


default_config = get_config()
DATABASE_URL = default_config.database_url
