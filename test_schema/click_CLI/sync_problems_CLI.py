import os
from sqlalchemy import Engine
from sqlmodel import Session, select, create_engine
from models.problem import Problem
from backend_client import create_problem

engine = create_engine(os.getenv("BACKEND_URL"))

def sync_problems():
    with Session(engine) as session:
        problems = session.exec(
            select(Problem).where(Problem.revision_id == None)
        ).all()
        for problem in problems:
            try:
                backend_problem = create_problem(problem)
            except Exception as e:
                print(f"Failed to create problem {problem.id} in backend: {e}")
                continue
            problem.revision_id = backend_problem["id"]
            session.add(problem)
        session.commit()


if __name__ == "__main__":
    sync_problems()
