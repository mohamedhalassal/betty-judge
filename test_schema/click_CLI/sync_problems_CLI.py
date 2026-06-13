import os
from sqlalchemy import Engine
from sqlmodel import Session, select, create_engine
from models.problem import Problem
from backend_client import create_problem
import click


engine = create_engine(os.getenv("DATABASE_URL"))

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

@click.command()
def main():
	click.echo("Syncing problems...")
	sync_problems()
	click.echo("Problems sync finished.")

if __name__ == "__main__":
    main()
