# todo if in production don't run this function
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from sqlmodel import SQLModel
from src.database import engine
from src.api.auth import router as auth_router
from src.api.problems import router as problems_router
from src.api.test_cases import router as test_cases_router
from src.api.judge import router as judge_router
app = FastAPI()
app.include_router(auth_router)
app.include_router(problems_router)
app.include_router(test_cases_router)
app.include_router(judge_router)
if __name__ == "__main__":
  pass
