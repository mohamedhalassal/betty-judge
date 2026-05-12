import os
from sqlmodel import create_engine
import src.models
from .core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
