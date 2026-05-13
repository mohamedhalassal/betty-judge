import os
import src.models
from .core.config import DATABASE_URL
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import create_engine, Session, SQLModel
from typing import Annotated

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]