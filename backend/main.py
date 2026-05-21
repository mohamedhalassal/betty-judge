# todo if in production don't run this function
from dotenv import load_dotenv
load_dotenv()

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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(problems_router)
app.include_router(test_cases_router)
app.include_router(submissions_router)

if __name__ == "__main__":
  pass
