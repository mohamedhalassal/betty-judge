from dotenv import load_dotenv
from sqlmodel import create_engine
import os

load_dotenv()

def get_engine():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return create_engine(database_url)