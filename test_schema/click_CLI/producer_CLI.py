import os
import sys
from pathlib import Path

import click
from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, select


REPO_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_DIR / "backend"
TEST_SCHEMA_DIR = REPO_DIR / "test_schema"

load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(TEST_SCHEMA_DIR))

from models.submission import Submission, SubmissionStatus


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in backend/.env")
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'").replace("\\&", "&")

engine = create_engine(DATABASE_URL)

SUBMISSION_STATUS_VALUES = [status.value for status in SubmissionStatus]


def get_queue() -> QueueClient:
    queue_name = os.getenv("AZURE_QUEUE_NAME")
    account_url = os.getenv("AZURE_QUEUE_ACCOUNT_URL")

    if not queue_name:
         raise RuntimeError("AZURE_QUEUE_NAME must be set in backend/.env")
    if not account_url:
        raise RuntimeError("AZURE_QUEUE_ACCOUNT_URL must be set in backend/.env")

    queue = QueueClient(
        account_url,
        queue_name=queue_name,
        credential=DefaultAzureCredential(),
    )

    try:
        queue.create_queue(timeout=5)
    except ResourceExistsError:
        pass

    return queue


def get_submissions(
    submission_ids: tuple[int, ...],
    problem_id: int | None,
    user_id: int | None,
    verdict: str | None,
    codeforces_verdict: str | None,
    codeforces_submission_id: int | None,
    limit: int | None,
) -> list[Submission]:
    statement = select(Submission)

    if submission_ids:
        statement = statement.where(Submission.id.in_(submission_ids))
    if problem_id is not None:
        statement = statement.where(Submission.problem_id == problem_id)
    if user_id is not None:
        statement = statement.where(Submission.user_id == user_id)
    if verdict is not None:
        statement = statement.where(Submission.verdict == SubmissionStatus(verdict))
    if codeforces_verdict is not None:
        statement = statement.where(
            Submission.codeforces_verdict == SubmissionStatus(codeforces_verdict)
        )
    if codeforces_submission_id is not None:
        statement = statement.where(
            Submission.codeforces_submission_id == codeforces_submission_id
        )

    statement = statement.order_by(Submission.id)
    if limit is not None:
        statement = statement.limit(limit)

    with Session(engine) as session:
        return list(session.exec(statement).all())


@click.command()
@click.option(
    "--submission-id",
    "submission_ids",
    type=int,
    multiple=True,
    help="Submission id to send. Can be used multiple times.",
)
@click.option("--problem-id", type=int, default=None, help="Filter by problem id.")
@click.option("--user-id", type=int, default=None, help="Filter by user id.")
@click.option(
    "--verdict",
    type=click.Choice(SUBMISSION_STATUS_VALUES),
    default=SubmissionStatus.IN_QUEUE.value,
    show_default=True,
    help="Filter by local verdict.",
)
@click.option(
    "--codeforces-verdict",
    type=click.Choice(SUBMISSION_STATUS_VALUES),
    default=None,
    help="Filter by Codeforces verdict.",
)
@click.option(
    "--codeforces-submission-id",
    type=int,
    default=None,
    help="Filter by Codeforces submission id.",
)
@click.option("--limit", type=int, default=None, help="Maximum submissions to send.")
def main(
    submission_ids,
    problem_id,
    user_id,
    verdict,
    codeforces_verdict,
    codeforces_submission_id,
    limit,
):
    queue = get_queue()
    submissions = get_submissions(
        submission_ids,
        problem_id,
        user_id,
        verdict,
        codeforces_verdict,
        codeforces_submission_id,
        limit,
    )

    sent = 0
    for submission in submissions:
        if submission.id is None:
            continue

        message = str(submission.id)
        queue.send_message(message, timeout=5)
        sent += 1
        print(f"Sent submission {submission.id}")

    print(f"Finished sending {sent} submission(s)")


if __name__ == "__main__":
    main()
