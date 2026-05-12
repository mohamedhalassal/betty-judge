# todo if in production don't run this function
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from sqlmodel import SQLModel
from src.database import engine
from src.api.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)

if __name__ == "__main__":
  pass
