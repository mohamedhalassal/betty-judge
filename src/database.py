import os
from sqlmodel import create_engine
import src.models
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
