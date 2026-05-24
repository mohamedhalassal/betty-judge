import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import update
from sqlmodel import Session, select


JUDGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(JUDGE_DIR))

from src.models.submission import Submission, SubmissionStatus
from src.runner import engine, judge_submission


def masked_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "")
    if "@" not in database_url:
        return database_url
    before_host = database_url.split("@", 1)[0]
    if ":" not in before_host:
        return database_url
    return database_url.replace(before_host.rsplit(":", 1)[-1], "***", 1)


def log(message: str = ""):
    print(message, flush=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run local judge on submissions and compare the result with "
            "codeforces_verdict."
        )
    )
    parser.add_argument(
        "--problem-id",
        type=int,
        default=None,
        help="Only check submissions for this local problem id.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of submissions to check.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=20,
        help="Start from this 1-based position in the selected submissions.",
    )
    parser.add_argument(
        "--ignore-local-tle",
        action="store_true",
        help="Ignore submissions where the local judge returns TLE.",
    )
    parser.add_argument(
        "--show-matches",
        action="store_true",
        help="Deprecated. Matches are always printed.",
    )
    return parser.parse_args()


def submissions_to_check(
    session: Session,
    problem_id: int | None,
    limit: int | None,
    start: int,
):
    statement = select(Submission).where(
        Submission.codeforces_verdict != SubmissionStatus.IN_QUEUE
    )
    if problem_id is not None:
        statement = statement.where(Submission.problem_id == problem_id)
    statement = statement.order_by(Submission.id)
    statement = statement.offset(max(0, start - 1))
    if limit is not None:
        statement = statement.limit(limit)
    return session.exec(statement).all()


def reset_submission_for_judge(session: Session, submission_id: int):
    session.exec(
        update(Submission)
        .where(Submission.id == submission_id)
        .values(
            verdict=SubmissionStatus.IN_QUEUE,
            execution_time=None,
            execution_memory=None,
        )
    )
    session.commit()


def main():
    args = parse_args()

    checked = 0
    matched = 0
    mismatched = 0
    ignored_local_tle = 0
    failed = 0

    with Session(engine) as session:
        log("Loading submissions from database...")
        submissions = submissions_to_check(
            session,
            args.problem_id,
            args.limit,
            args.start,
        )
        log(f"Found {len(submissions)} submission(s) to check.")

        for index, submission in enumerate(submissions, start=1):
            submission_id = submission.id
            if submission_id is None:
                continue

            log(f"[{index}/{len(submissions)}] Running submission {submission_id}")
            reset_submission_for_judge(session, submission_id)

            try:
                message = judge_submission(session, submission_id)
            except Exception as exc:
                failed += 1
                log(f"  FAILED: {exc}")
                continue

            session.expire_all()
            judged_submission = session.get(Submission, submission_id)
            if judged_submission is None:
                failed += 1
                log("  FAILED: submission disappeared after judging")
                continue

            local_verdict = judged_submission.verdict
            codeforces_verdict = judged_submission.codeforces_verdict

            if (
                local_verdict == SubmissionStatus.TIME_LIMIT_EXCEEDED
                and args.ignore_local_tle
            ):
                ignored_local_tle += 1
                log(
                    f"  Result: IGNORED local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value} | Message: {message}"
                )
                continue

            checked += 1
            if local_verdict == codeforces_verdict:
                matched += 1
                log(
                    f"  Result: MATCH local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value} | Message: {message}"
                )
            else:
                mismatched += 1
                log(
                    f"  Result: MISMATCH local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value} | Message: {message}"
                )

    log()
    log("Summary")
    log(f"  Compared: {checked}")
    log(f"  Matched: {matched}")
    log(f"  Mismatched: {mismatched}")
    log(f"  Ignored local TLE: {ignored_local_tle}")
    log(f"  Failed to run: {failed}")


if __name__ == "__main__":
    main()
