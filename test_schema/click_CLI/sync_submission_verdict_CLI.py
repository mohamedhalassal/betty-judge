import os
import time
import requests
from sqlmodel import Session, select, create_engine
from backend_client import BASE_URL, HEADERS, create_submission
from models.problem import Problem
from models.submission import Submission, SubmissionStatus
import click
from database import get_engine


def sync_submissions():
    with Session(get_engine()) as session:
        statement = (
            select(Submission)
            .where(
                Submission.revision_id is not None,
                Submission.verdict == SubmissionStatus.IN_QUEUE,
            )
            .order_by(Submission.revision_id) 
        )

        results = session.exec(statement).all()
        for submission in results:
            try:
                response = requests.get(
                    f"{BASE_URL}/my-submissions/{submission.id}",
                    headers=HEADERS,
                    timeout=30,
                )
                response.raise_for_status()
                backend_submission = response.json()
                if backend_submission["verdict"] == SubmissionStatus.IN_QUEUE:
                    print(f"Submission {submission.id} is still in queue, retring.")
                    time.sleep(5)
                    backend_submission = requests.get(
                        f"{BASE_URL}/my-submissions/{submission.id}",
                        headers=HEADERS,
                        timeout=30,
                    )
                    response.raise_for_status()
                

                submission.verdict = backend_submission["verdict"]
                submission.execution_time = backend_submission["execution_time"]
                # submission.execution_memory = backend_submission["execution_memory"]

            except Exception as e:
                print(f"Failed to create submission {submission.id} in backend: {e}")
                continue
            session.add(submission)
        session.commit()


@click.command()
def main():
    click.echo("Syncing submissions...")
    sync_submissions()
    click.echo("Submissions sync finished.")


if __name__ == "__main__":
    main()
