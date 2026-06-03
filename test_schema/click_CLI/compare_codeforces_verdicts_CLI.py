import os
import re
import sys
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import click
from dotenv import load_dotenv
from sqlalchemy import update
from sqlmodel import Session, create_engine, select


REPO_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_DIR / "backend"
TEST_SCHEMA_DIR = REPO_DIR / "test_schema"
JUDGE_DIR = REPO_DIR / "judge"
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(TEST_SCHEMA_DIR))

from models.submission import Submission, SubmissionStatus


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in backend/.env")
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'").replace("\\&", "&")
engine = create_engine(DATABASE_URL)


from confluent_kafka import Producer #pyright: ignore
from confluent_kafka.admin import AdminClient, NewTopic  # pyright: ignore

KAFKA_TOPIC = "submissions"
KAFKA_PARTITIONS = 8

producer_config = {
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
}

producer = Producer(producer_config)

def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} : partition {msg.partition()} : at offset {msg.offset()}")

admin = AdminClient({
    "bootstrap.servers": "localhost:9092"
})


def create_submissions_topic():
    metadata = admin.list_topics(timeout=10)
    if KAFKA_TOPIC in metadata.topics:
        return

    result = admin.create_topics([
        NewTopic(KAFKA_TOPIC, num_partitions=KAFKA_PARTITIONS, replication_factor=1)
    ])
    result[KAFKA_TOPIC].result()
    log(f"✅ Created topic {KAFKA_TOPIC} with {KAFKA_PARTITIONS} partitions")


def send_submission_to_kafka(submission_id: int):
    event = {
        "event_type": "SUBMISSION_CREATED",
        "submission_id": submission_id,
    }
    producer.produce(
        KAFKA_TOPIC,
        key=str(submission_id),
        value=json.dumps(event).encode("utf-8"),
        callback=delivery_report,
    )
    producer.flush()

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


def parse_failed_test(message: str | None) -> int | None:
    if not message:
        return None
    match = re.search(r"\bon\s+test:\s*(\d+)\b", message, re.IGNORECASE)
    return int(match.group(1)) if match else None


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
    message: str,
    is_mismatch: bool,
):
    local_failed_test = parse_failed_test(message)
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


def run_submission_in_docker(
    runner_url: str,
    submission_id: int,
    request_timeout: int,
) -> tuple[str, list[dict]]:
    query = urllib.parse.urlencode(
        {"submission_id": submission_id, "include_testcase_results": "true"}
    )
    url = f"{runner_url.rstrip('/')}/runner?{query}"
    request = urllib.request.Request(url, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        raise RuntimeError(f"Docker runner returned HTTP {error.code}: {body}") from None
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not reach Docker runner at {runner_url}. "
            "Start the judge container and publish port 8000."
        ) from error

    try:
        parsed_body = json.loads(body)
    except json.JSONDecodeError:
        return body, []
    if isinstance(parsed_body, str):
        return parsed_body, []
    if isinstance(parsed_body, dict):
        message = parsed_body.get("message")
        testcases = parsed_body.get("testcases", [])
        return (
            message if isinstance(message, str) else json.dumps(parsed_body),
            testcases if isinstance(testcases, list) else [],
        )
    return json.dumps(parsed_body), []


def log_testcase_results(testcases: list[dict]):
    for testcase in testcases:
        testcase_number = testcase.get("number")
        testcase_id = testcase.get("id")
        status = testcase.get("status", "-")
        time_ms = testcase.get("time_ms")
        memory_mb = testcase.get("memory_mb")
        log(
            "  Testcase "
            f"{format_optional_int(testcase_number)} "
            f"(id={format_optional_int(testcase_id)}): "
            f"{status} | "
            f"time={format_ms(time_ms)} "
            f"memory={format_mb(memory_mb)}"
        )


def parse_local_runner_response(response) -> tuple[str, list[dict]]:
    if isinstance(response, str):
        return response, []
    if isinstance(response, dict):
        message = response.get("message")
        testcases = response.get("testcases", [])
        return (
            message if isinstance(message, str) else json.dumps(response),
            testcases if isinstance(testcases, list) else [],
        )
    return str(response), []


def run_submission_locally(session: Session, submission_id: int) -> tuple[str, list[dict]]:
    import types

    sys.path.insert(0, str(JUDGE_DIR))
    from models import problem as test_problem
    from models import submission as test_submission
    from models import test_case as test_test_case

    src_models = types.ModuleType("src.models")
    src_models.__path__ = []
    sys.modules.update(
        {
            "src.models": src_models,
            "src.models.problem": test_problem,
            "src.models.submission": test_submission,
            "src.models.test_case": test_test_case,
        }
    )

    from src.runner import judge_submission

    return parse_local_runner_response(
        judge_submission(session, submission_id, include_testcase_results=True)
    )


@click.command()
@click.option(
    "--problem-id",
    type=int,
    default=None,
    help="Only check submissions for this local problem id.",
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
    help="Ignore submissions where the local judge returns TLE.",
)
@click.option(
    "--show-matches",
    "_show_matches",
    is_flag=True,
    help="Deprecated. Matches are always printed.",
)
@click.option(
    "--runner-url",
    default="http://127.0.0.1:8000",
    show_default=True,
    help="Docker judge runner base URL.",
)
@click.option(
    "--request-timeout",
    type=int,
    default=300,
    show_default=True,
    help="Timeout in seconds for each Docker runner request.",
)
@click.option(
    "--local-runner",
    is_flag=True,
    help="Run judge_submission in this Python process instead of calling Docker.",
)
@click.option(
    "--kafka-producer/--no-kafka-producer",
    default=True,
    show_default=True,
    help="Send selected submissions to Kafka instead of running the judge.",
)
def compare_codeforces_verdicts(
    problem_id,
    limit,
    start,
    ignore_local_tle,
    _show_matches,
    runner_url,
    request_timeout,
    local_runner,
    kafka_producer,
):
    """Run local judge on submissions and compare with Codeforces verdicts."""
    checked = 0
    matched = 0
    mismatched = 0
    ignored_local_tle = 0
    failed = 0
    produced = 0

    if kafka_producer:
        create_submissions_topic()

    with Session(engine) as session:
        log("Loading submissions from database...")
        submissions = submissions_to_check(
            session,
            problem_id,
            limit,
            start,
        )
        log(f"Found {len(submissions)} submission(s) to check.")

        for index, submission in enumerate(submissions, start=1):
            submission_id = submission.id
            if submission_id is None:
                continue

            log(f"[{index}/{len(submissions)}] Running submission {submission_id}")
            reset_submission_for_judge(session, submission_id)

            if kafka_producer:
                send_submission_to_kafka(submission_id)
                produced += 1
                continue

            try:
                if local_runner:
                    message, testcase_results = run_submission_locally(
                        session,
                        submission_id,
                    )
                else:
                    message, testcase_results = run_submission_in_docker(
                        runner_url,
                        submission_id,
                        request_timeout,
                    )
                log_testcase_results(testcase_results)
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
                and ignore_local_tle
            ):
                ignored_local_tle += 1
                log(
                    f"  Result: IGNORED local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value} | Message: {message}"
                )
                log_comparison_details(judged_submission, message, False)
                continue

            checked += 1
            if local_verdict == codeforces_verdict:
                matched += 1
                log(
                    f"  Result: MATCH local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value} | Message: {message}"
                )
                log_comparison_details(judged_submission, message, False)
            else:
                mismatched += 1
                log(
                    f"  Result: MISMATCH local={local_verdict.value} "
                    f"codeforces={codeforces_verdict.value} | Message: {message}"
                )
                log_comparison_details(judged_submission, message, True)

    log()
    log("Summary")
    if kafka_producer:
        log(f"  Produced to Kafka: {produced}")
        return

    log(f"  Compared: {checked}")
    log(f"  Matched: {matched}")
    log(f"  Mismatched: {mismatched}")
    log(f"  Matched - mismatched: {matched - mismatched}")
    log(f"  Ignored local TLE: {ignored_local_tle}")
    log(f"  Failed to run: {failed}")


if __name__ == "__main__":
    compare_codeforces_verdicts()
