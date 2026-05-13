import os

ENV = os.getenv("ENV", "development")

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
if CLIENT_ID is None or CLIENT_ID == "":
    raise ValueError("GOOGLE_CLIENT_ID environment variable is not set")

CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
if CLIENT_SECRET is None or CLIENT_SECRET == "":
    raise ValueError("GOOGLE_CLIENT_SECRET environment variable is not set")
 
DATABASE_URL = os.environ.get("DATABASE_URL")
if ENV == "development" and (DATABASE_URL is None or DATABASE_URL == ""):
    DATABASE_URL = "sqlite://./database.db"

if DATABASE_URL is None or DATABASE_URL == "":
    raise ValueError("DATABASE_URL environment variable is not set")
