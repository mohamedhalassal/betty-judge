import os
import sys
import time
from pathlib import Path
from typing import Any

import click
from sqlalchemy import func
from dotenv import load_dotenv
from sqlmodel import Session, select

REPO_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_DIR / "backend"
TEST_SCHEMA_DIR = REPO_DIR / "test_schema"

load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(TEST_SCHEMA_DIR))

from backend_client import get_submission
from database import get_engine
from models.submission import Submission, SubmissionStatus


def backend_verdict_to_submission_status(
    verdict: str | None,
) -> SubmissionStatus | None:
    if verdict is None:
        return None

    normalized_verdict = verdict.strip().lower().replace("_", " ")
    try:
        return SubmissionStatus(normalized_verdict)
    except ValueError:
        raise ValueError(f"Unknown backend verdict: {verdict}") from None


def update_submission_from_backend(
    submission: Submission,
    backend_submission: dict[str, Any],
) -> bool:
    changed = False

    backend_status = backend_verdict_to_submission_status(
        backend_submission.get("verdict")
    )
    if backend_status is not None and submission.verdict != backend_status:
        submission.verdict = backend_status
        changed = True

    backend_execution_time = backend_submission.get("execution_time")
    if submission.execution_time != backend_execution_time:
        submission.execution_time = backend_execution_time
        changed = True

    backend_execution_memory = backend_submission.get("execution_memory")
    if submission.execution_memory != backend_execution_memory:
        submission.execution_memory = backend_execution_memory
        changed = True

    return changed


def echo_backend_submission(
    local_submission_id: int,
    backend_submission_id: int,
    backend_submission: dict[str, Any],
):
    click.echo(
        "Fetched local submission "
        f"{local_submission_id} -> backend revision "
        f"{backend_submission_id}: "
        f"verdict={backend_submission.get('verdict')}, "
        f"time={backend_submission.get('execution_time')}, "
        f"memory={backend_submission.get('execution_memory')}"
    )


def get_backend_submission_until_finished(
    local_submission_id: int,
    backend_submission_id: int,
    poll_interval_seconds: int,
) -> dict[str, Any] | None:
    while True:
        try:
            backend_submission = get_submission(backend_submission_id)
        except Exception as exc:
            click.echo(
                "Failed to fetch backend submission "
                f"{backend_submission_id} for local submission "
                f"{local_submission_id}: {exc}"
            )
            return None

        echo_backend_submission(
            local_submission_id,
            backend_submission_id,
            backend_submission,
        )

        backend_status = backend_verdict_to_submission_status(
            backend_submission.get("verdict")
        )
        if backend_status != SubmissionStatus.IN_QUEUE:
            return backend_submission

        click.echo(
            "Backend submission "
            f"{backend_submission_id} is still in queue. "
            f"Sleeping {poll_interval_seconds} seconds before asking again..."
        )
        time.sleep(poll_interval_seconds)


def sync_in_queue_submissions(
    limit: int | None,
    dry_run: bool,
    poll_interval_seconds: int,
) -> tuple[int, int]:
    checked_count = 0
    updated_count = 0

    with Session(get_engine()) as session:
        statement = select(Submission).where(
            Submission.verdict == SubmissionStatus.IN_QUEUE,
            Submission.revision_id != None,
        )
        statement = statement.order_by(Submission.id)
        if limit is not None:
            statement = statement.limit(limit)

        submissions = session.exec(statement).all()
        click.echo(
            "Found "
            f"{len(submissions)} local in-queue submission(s) with revision_id."
        )
        if not submissions:
            in_queue_count = session.exec(
                select(func.count())
                .select_from(Submission)
                .where(Submission.verdict == SubmissionStatus.IN_QUEUE)
            ).one()
            in_queue_without_revision_count = session.exec(
                select(func.count())
                .select_from(Submission)
                .where(
                    Submission.verdict == SubmissionStatus.IN_QUEUE,
                    Submission.revision_id == None,
                )
            ).one()
            with_revision_count = session.exec(
                select(func.count())
                .select_from(Submission)
                .where(Submission.revision_id != None)
            ).one()
            click.echo(
                "Scan summary: "
                f"in_queue={in_queue_count}, "
                f"in_queue_without_revision_id={in_queue_without_revision_count}, "
                f"with_revision_id={with_revision_count}"
            )

        for submission in submissions:
            if submission.id is None or submission.revision_id is None:
                continue

            checked_count += 1
            backend_submission = get_backend_submission_until_finished(
                submission.id,
                submission.revision_id,
                poll_interval_seconds,
            )
            if backend_submission is None:
                continue

            try:
                changed = update_submission_from_backend(
                    submission, backend_submission
                )
            except Exception as exc:
                click.echo(
                    "Failed to apply backend submission "
                    f"{submission.revision_id} to local submission "
                    f"{submission.id}: {exc}"
                )
                continue

            if changed:
                updated_count += 1
                if not dry_run:
                    session.add(submission)

        if updated_count and not dry_run:
            session.commit()

    return checked_count, updated_count


@click.command()
@click.option("--limit", type=int, default=None, help="Maximum submissions to sync.")
@click.option(
    "--backend-url",
    default=None,
    envvar="BACKEND_URL",
    help="Backend base URL. Can also be set with BACKEND_URL.",
)
@click.option(
    "--backend-user-token",
    default=None,
    envvar="BACKEND_USER_TOKEN",
    help="Backend bearer token. Can also be set with BACKEND_USER_TOKEN.",
)
@click.option(
    "--poll-interval-seconds",
    type=int,
    default=5,
    show_default=True,
    help="Seconds to sleep before refetching a backend submission still in queue.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Fetch backend submissions without updating the local database.",
)
def main(
    limit: int | None,
    backend_url: str | None,
    backend_user_token: str | None,
    poll_interval_seconds: int,
    dry_run: bool,
):
    if backend_url:
        os.environ["BACKEND_URL"] = backend_url
    if backend_user_token:
        os.environ["BACKEND_USER_TOKEN"] = backend_user_token

    click.echo("Syncing local in-queue submissions from backend...")
    checked_count, updated_count = sync_in_queue_submissions(
        limit,
        dry_run,
        poll_interval_seconds,
    )
    if dry_run:
        click.echo(
            "Dry run finished. "
            f"Checked {checked_count} submission(s), "
            f"{updated_count} would be updated."
        )
    else:
        click.echo(
            "Sync finished. "
            f"Checked {checked_count} submission(s), "
            f"updated {updated_count}."
        )


if __name__ == "__main__":
    main()
