import os
from sqlmodel import Session, select, create_engine
from backend_client import create_submission
from models.problem import Problem
from models.submission import Submission
import click


engine = create_engine(os.getenv("BACKEND_URL"))

def sync_submissions():
    with Session(engine) as session:
        submissions = session.exec(
            select(Submission).where(Submission.revision_id == None)
        ).all()
        for submission in submissions:
            problem = session.get(Problem, submission.problem_id)
            if problem is None:
                continue
            if problem.revision_id is None:
                continue
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
