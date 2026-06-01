# todo if in production don't run this function
from dotenv import load_dotenv
load_dotenv()
import sys
from pathlib import Path
from fastapi import FastAPI
# from sqlmodel import SQLModel
# from src.database import engine
# from src.api.auth import router as auth_router
# from src.api.problems import router as problems_router
from src.runner import router as runner_router
app = FastAPI()
app.include_router(runner_router)

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(BACKEND_DIR))

# app.include_router(problems_router)
# app.include_router(test_cases_router)
if __name__ == "__main__":
  pass
