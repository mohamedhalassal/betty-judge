# todo if in production don't run this function
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
from src.database import create_db_and_tables

from fastapi import FastAPI
from sqlmodel import SQLModel
from src.database import engine
from src.api.auth import router as auth_router
from src.api.problems import router as problems_router
from src.api.test_cases import router as test_cases_router
from src.api.submissions import router as submissions_router
from src.api.get_problem_from_polygon import router as polygon_router
app = FastAPI()
app.include_router(auth_router)
app.include_router(problems_router)
app.include_router(test_cases_router)
app.include_router(submissions_router)
app.include_router(polygon_router)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
if __name__ == "__main__":
  pass
