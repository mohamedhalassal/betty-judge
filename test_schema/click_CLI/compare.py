import os
import sys
from pathlib import Path

import click
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


def masked_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "")
    if "@" not in database_url:
        return database_url
    before_host = database_url.split("@", 1)[0]
    if ":" not in before_host:
        return database_url
    return database_url.replace(before_host.rsplit(":", 1)[-1], "***", 1)


def log(message: str = ""):
    click.echo(message)


def format_optional_int(value: int | None) -> str:
    return str(value) if value is not None else "-"


def format_ms(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{value:.0f} ms"


def format_signed_ms(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{value:+.0f} ms"


def bytes_to_mb(value: int | None) -> float | None:
    if value is None:
        return None
    return value / (1024 * 1024)


def format_mb(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{value:.2f} MB"


def format_signed_mb(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{value:+.2f} MB"


def diff_values(
    local_value: float | int | None,
    codeforces_value: float | int | None,
) -> float | None:
    if local_value is None or codeforces_value is None:
        return None
    return local_value - codeforces_value


def log_comparison_details(
    submission: Submission,
    is_mismatch: bool,
):
    local_failed_test = submission.local_failed_test
    codeforces_memory_mb = bytes_to_mb(submission.codeforces_memory_bytes)
    time_diff = diff_values(submission.execution_time, submission.codeforces_time_ms)
    memory_diff = diff_values(submission.execution_memory, codeforces_memory_mb)

    log(
        "  Codeforces submission: "
        f"{format_optional_int(submission.codeforces_submission_id)}"
    )
    log(
        "  Codeforces failed test: "
        f"{format_optional_int(submission.codeforces_failed_test)}"
    )
    if is_mismatch:
        log(
            "  Mismatch details: "
            f"local={submission.verdict.value} "
            f"test={format_optional_int(local_failed_test)} | "
            f"codeforces={submission.codeforces_verdict.value} "
            f"test={format_optional_int(submission.codeforces_failed_test)}"
        )
    log(
        "  Time: "
        f"local={format_ms(submission.execution_time)} | "
        f"codeforces={format_ms(submission.codeforces_time_ms)} | "
        f"diff={format_signed_ms(time_diff)}"
    )
    log(
        "  Memory: "
        f"local={format_mb(submission.execution_memory)} | "
        f"codeforces={format_mb(codeforces_memory_mb)} | "
        f"diff={format_signed_mb(memory_diff)}"
    )


def submissions_to_check(
    session: Session,
    submission_ids: tuple[int, ...],
    problem_id: int | None,
    user_id: int | None,
    verdict: str | None,
    codeforces_verdict: str | None,
    codeforces_submission_id: int | None,
    limit: int | None,
    start: int,
):
    statement = select(Submission)
    if submission_ids:
        statement = statement.where(Submission.id.in_(submission_ids))
    if problem_id is not None:
        statement = statement.where(Submission.problem_id == problem_id)
    if user_id is not None:
        statement = statement.where(Submission.user_id == user_id)
    if verdict is not None:
        statement = statement.where(Submission.verdict == SubmissionStatus(verdict))
    else:
        statement = statement.where(Submission.verdict != SubmissionStatus.IN_QUEUE)
    if codeforces_verdict is not None:
        statement = statement.where(
            Submission.codeforces_verdict == SubmissionStatus(codeforces_verdict)
        )
    else:
        statement = statement.where(
            Submission.codeforces_verdict != SubmissionStatus.IN_QUEUE
        )
    if codeforces_submission_id is not None:
        statement = statement.where(
            Submission.codeforces_submission_id == codeforces_submission_id
        )
    statement = statement.order_by(Submission.id)
    statement = statement.offset(max(0, start - 1))
    if limit is not None:
        statement = statement.limit(limit)
    return session.exec(statement).all()


@click.command()
@click.option(
    "--submission-id",
    "submission_ids",
    type=int,
    multiple=True,
    help="Submission id to compare. Can be used multiple times.",
)
@click.option(
    "--problem-id",
    type=int,
    default=None,
    help="Only check submissions for this local problem id.",
)
@click.option("--user-id", type=int, default=None, help="Filter by user id.")
@click.option(
    "--verdict",
    type=click.Choice(SUBMISSION_STATUS_VALUES),
    default=None,
    help="Filter by local verdict.",
)
@click.option(
    "--codeforces-verdict",
    type=click.Choice(SUBMISSION_STATUS_VALUES),
    default=None,
    help="Filter by Codeforces verdict. Defaults to any non-queue verdict.",
)
@click.option(
    "--codeforces-submission-id",
    type=int,
    default=None,
    help="Filter by Codeforces submission id.",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Maximum number of submissions to check.",
)
@click.option(
    "--start",
    type=int,
    default=1,
    show_default=True,
    help="Start from this 1-based position in the selected submissions.",
)
@click.option(
    "--ignore-local-tle",
    is_flag=True,
    help="Ignore submissions where the stored local verdict is TLE.",
)
@click.option(
    "--show-matches",
    "_show_matches",
    is_flag=True,
    help="Deprecated. Matches are always printed.",
)
def compare(
    submission_ids,
    problem_id,
    user_id,
    verdict,
    codeforces_verdict,
    codeforces_submission_id,
    limit,
    start,
    ignore_local_tle,
    _show_matches,
):
    """Compare local and Codeforces verdicts already stored in the database."""
    checked = 0
    matched = 0
    mismatched = 0
    ignored_local_tle = 0

    with Session(engine) as session:
        log("Loading submissions from database...")
        submissions = submissions_to_check(
            session,
            submission_ids,
            problem_id,
            user_id,
            verdict,
            codeforces_verdict,
            codeforces_submission_id,
            limit,
            start,
        )
        log(f"Found {len(submissions)} submission(s) to compare.")

        for index, submission in enumerate(submissions, start=1):
            submission_id = submission.id
            if submission_id is None:
                continue

            log(f"[{index}/{len(submissions)}] Comparing submission {submission_id}")
            local_verdict = submission.verdict
            codeforces_verdict = submission.codeforces_verdict

            if (
                local_verdict == SubmissionStatus.TIME_LIMIT_EXCEEDED
                and ignore_local_tle
            ):
                ignored_local_tle += 1
                log(
                    f"  Result: IGNORED local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value}"
                )
                log_comparison_details(submission, False)
                continue

            checked += 1
            if local_verdict == codeforces_verdict:
                matched += 1
                log(
                    f"  Result: MATCH local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value}"
                )
                log_comparison_details(submission, False)
            else:
                mismatched += 1
                log(
                    f"  Result: MISMATCH local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value}"
                )
                log_comparison_details(submission, True)

    log()
    log("Summary")
    log(f"  Compared: {checked}")
    log(f"  Matched: {matched}")
    log(f"  Mismatched: {mismatched}")
    log(f"  Ignored local TLE: {ignored_local_tle}")


if __name__ == "__main__":
    compare()
