import os

from pydantic import BaseModel

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

class EnvConfig(BaseModel):
    is_prod: bool = ENV == "production"
    client_id: str = CLIENT_ID
    jwt_secret_key: str = JWT_SECRET_KEY
    database_url: str = DATABASE_URL

default_config = EnvConfig()