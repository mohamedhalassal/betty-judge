import os
from sqlmodel import Session, select, create_engine
from backend_client import create_submission
from models.problem import Problem
from models.submission import Submission
import click

engine = create_engine(os.getenv("DATABASE_URL"))


def sync_submissions():
    with Session(engine) as session:
        statement = (
            select(Submission, Problem)
            .join(Problem, Submission.problem_id == Problem.id)
            .where(
                Submission.revision_id == None,
                Problem.revision_id != None,
            )
        )
        results = session.exec(statement).all()
        for submission,problem in results:
            try:
                backend_submission = create_submission(
                    problem.revision_id, submission.source_code
                )
            except Exception as e:
                print(f"Failed to create submission {submission.id} in backend: {e}")
                continue
            submission.revision_id = backend_submission["id"]
            session.add(submission)
        session.commit()


@click.command()
def main():
    click.echo("Syncing submissions...")
    sync_submissions()
    click.echo("Submissions sync finished.")


if __name__ == "__main__":
    main()
