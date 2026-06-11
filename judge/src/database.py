import os

from sqlmodel import Session, create_engine


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set in backend/.env")

    return database_url.strip().strip('"').strip("'").replace("\\&", "&")


engine = create_engine(get_database_url())


def get_session() -> Session:
    return Session(engine)