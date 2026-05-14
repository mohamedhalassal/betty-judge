# todo if in production don't run this function
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from sqlmodel import SQLModel
from src.database import engine
from src.api.auth import router as auth_router
from src.api.crud import router as problems_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(problems_router)

if __name__ == "__main__":
  pass
