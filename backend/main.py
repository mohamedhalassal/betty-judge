# todo if in production don't run this function
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")
from src.database import create_db_and_tables


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from src.database import engine
from src.api.auth import router as auth_router
from src.api.problems import router as problems_router
from src.api.test_cases import router as test_cases_router
from src.api.submissions import router as submissions_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(problems_router)
app.include_router(test_cases_router)
app.include_router(submissions_router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    

if __name__ == "__main__":
    pass
