import subprocess
import tempfile
import resource
import math
import signal
import os
import sys
import json
import time
import threading
import platform
from datetime import datetime
from pathlib import Path
from typing import Annotated

REPO_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_DIR / "judge"))

from fastapi import Body, Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy import update
from sqlmodel import create_engine, Session, SQLModel, select
from src.models.submission import Submission
from src.models.problem import Problem
from src.models.test_case import TestCase
from src.models.submission import SubmissionStatus
from dotenv import load_dotenv

# from src.models.problem import Problem
# from src.models.user import User
# from src.models.test_case import TestCase
# from src.schemas.submission import SubmissionCreate, SubmissionResponse
# from src.models.submission import Submission
# from src.database import SessionDep, create_db_and_tables
# from src.core.security import verify_access_token, get_current_user

load_dotenv(REPO_DIR / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in backend/.env")
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'").replace("\\&", "&")
engine = create_engine(DATABASE_URL)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "submissions")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "judge-workers")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()


def normalize_source_code(source_code: str) -> str:
    return (
        source_code.replace("\ufeff", "")
        .replace("\u00a0", " ")
        .replace("\u2007", " ")
        .replace("\u202f", " ")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u200e", "")
        .replace("\u200f", "")
    )


def validation(session: Session, submission_id: int):
    # Check if the submission exists
    submission = session.exec(
        select(Submission).where(Submission.id == submission_id)
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check if the submission verdict is "in queue"
    if submission.verdict != SubmissionStatus.IN_QUEUE:
        raise HTTPException(
            status_code=400, detail="Submission verdict is not in queue"
        )

    # Check if the problem exists
    problem = session.exec(
        select(Problem).where(Problem.id == submission.problem_id)
    ).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return submission, problem


def finish_submission(
    session: Session,
    submission_id: int,
    verdict: SubmissionStatus,
    message: str,
    execution_time: float | None = None,
    execution_memory: float | None = None,
):
    session.exec(
        update(Submission)
        .values(
            verdict=verdict,
            execution_time=execution_time,
            execution_memory=execution_memory,
        )
        .where(
            (Submission.id == submission_id)
            & (Submission.verdict == SubmissionStatus.IN_QUEUE)
        )
    )
    session.commit()
    return message


def max_rss_to_mb(max_rss: int) -> float:
    return max_rss / 1024


def runner_response(message: str, testcases: list[dict], include_testcase_results: bool):
    if not include_testcase_results:
        return message
    return {"message": message, "testcases": testcases}


def add_testcase_result(
    testcases: list[dict],
    number: int,
    test_case: TestCase,
    status: str,
    time_ms: float,
    memory_mb: float,
):
    testcases.append(
        {
            "id": test_case.id,
            "number": number,
            "status": status,
            "time_ms": time_ms,
            "memory_mb": memory_mb,
        }
    )


def submission_id_from_event(event: dict) -> int:
    submission_id = event.get("submission_id")
    if submission_id is None and isinstance(event.get("data"), dict):
        submission_id = event["data"].get("submission_id")
    if submission_id is None:
        raise ValueError("Kafka event does not contain submission_id")
    return int(submission_id)


def run_worker():
    from confluent_kafka import Consumer

    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": KAFKA_CONSUMER_GROUP,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([KAFKA_TOPIC])
    print(
        f"Judge worker listening on topic {KAFKA_TOPIC} "
        f"as group {KAFKA_CONSUMER_GROUP}"
    )

    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                print(f"Kafka error: {message.error()}")
                continue

            try:
                event = json.loads(message.value().decode("utf-8"))
                submission_id = submission_id_from_event(event)
                print(
                    f"Judging submission {submission_id} "
                    f"from partition {message.partition()} offset {message.offset()}"
                )
                with Session(engine) as session:
                    result = judge_submission(session, submission_id)
                    print(f"Finished submission {submission_id}: {result}")
            except HTTPException as exc:
                print(
                    f"Skipped submission event at offset {message.offset()}: "
                    f"HTTP {exc.status_code} {exc.detail}"
                )
            except Exception as exc:
                print(f"Failed to handle event at offset {message.offset()}: {exc}")
    finally:
        consumer.close()


@router.post("/runner", status_code=201)
def judge_submission(
    session: SessionDep,
    submission_id: int,
    include_testcase_results: bool = False,
):
    submission, problem = validation(session, submission_id)
    testcase_results = []

    # compile the code
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_file = temp_path / "main.cpp"
        exe_file = temp_path / "main"
        # write given source code to file
        source_code = normalize_source_code(submission.source_code)
        source_file.write_text(source_code)
        # compile
        compile_result = subprocess.run(
            ["g++", "-std=gnu++20", "-O2", "-DONLINE_JUDGE", str(source_file), "-o", str(exe_file)],
            capture_output=True,
            text=True,
        )
        # todo : what should i return ?

        # compilation error
        if compile_result.returncode != 0:
            message = f"Compile error: {compile_result.stderr}"
            finish_submission(
                session,
                submission_id,
                SubmissionStatus.COMPILE_ERROR,
                message,
                execution_time=0,
                execution_memory=0,
            )
            return runner_response(message, testcase_results, include_testcase_results)
        execution_time = 0
        memory_usage = 0

        # run the executable with each test case and compare output
        cpu_limit_seconds = max(1, math.ceil(problem.time_limit / 1000))

        maxMemory = (
            problem.memory_limit * 1024 * 1024 * 5
        )  # Convert MB to bytes for RLIMIT_AS

        def limit_resources():
            try:
                resource.setrlimit(
                    resource.RLIMIT_CPU, (cpu_limit_seconds, cpu_limit_seconds + 2)
                )
            except (OSError, ValueError):
                pass

            try:
                resource.setrlimit(resource.RLIMIT_AS, (maxMemory, maxMemory))
            except (OSError, ValueError):
                pass

        test_case_number = 0
        last_test_case_id = 0

        while True:
            test_case = session.exec(
                select(TestCase)
                .where(TestCase.problem_id == submission.problem_id)
                .where(TestCase.id > last_test_case_id)
                .order_by(TestCase.id)
                .limit(1)
            ).first()
            if test_case is None:
                break
            test_case_number += 1
            last_test_case_id = test_case.id

            # run the executable with the test case input
            process = subprocess.Popen(
                [str(exe_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=limit_resources,
                start_new_session=True,
            )

            # set a wall clock time limit
            wall_limit_seconds = cpu_limit_seconds * 3 + 5
            wall_timed_out = False

            def kill_process():
                nonlocal wall_timed_out
                wall_timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

            timer = threading.Timer(wall_limit_seconds, kill_process)
            timer.start()

            try:
                try:
                    process.stdin.write(test_case.input_data)
                except BrokenPipeError:
                    pass
                finally:
                    try:
                        process.stdin.close()
                    except BrokenPipeError:
                        pass
            except OSError:
                pass

            try:
                pid, status, usage = os.wait4(process.pid, 0)
            finally:
                timer.cancel()

            process.returncode = os.waitstatus_to_exitcode(status)
            cpu_time = int((usage.ru_utime + usage.ru_stime) * 1000)
            memory_mb = int(max_rss_to_mb(usage.ru_maxrss))
            current_execution_time = max(execution_time, cpu_time)
            current_memory_usage = max(memory_usage, memory_mb)

            if wall_timed_out:
                message = f"Idleness Limit Exceeded on test: {test_case_number}"
                add_testcase_result(
                    testcase_results,
                    test_case_number,
                    test_case,
                    SubmissionStatus.IDLENESS_LIMIT_EXCEEDED.value,
                    cpu_time,
                    memory_mb,
                )
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.IDLENESS_LIMIT_EXCEEDED,
                    message,
                    execution_time=current_execution_time,
                    execution_memory=current_memory_usage,
                )
                return runner_response(message, testcase_results, include_testcase_results)  
            # time limit exceeded and runtime error and memory limit exceeded cases after signal
            if process.returncode != 0:
                sig = -process.returncode
                # time limit exceeded case
                if sig == signal.SIGXCPU or (
                    sig == signal.SIGKILL
                    and usage.ru_utime + usage.ru_stime >= cpu_limit_seconds
                ):
                    message = f"Time Limit Exceeded on test: {test_case_number}"
                    add_testcase_result(
                        testcase_results,
                        test_case_number,
                        test_case,
                        SubmissionStatus.TIME_LIMIT_EXCEEDED.value,
                        cpu_time,
                        memory_mb,
                    )
                    finish_submission(
                        session,
                        submission_id,
                        SubmissionStatus.TIME_LIMIT_EXCEEDED,
                        message,
                        execution_time=problem.time_limit,
                        execution_memory=current_memory_usage,
                    )
                    return runner_response(message, testcase_results, include_testcase_results)
                stderr_lower = process.stderr.read().lower()

                #  clear MLE cases
                if (
                    "bad_alloc" in stderr_lower
                    or "cannot allocate memory" in stderr_lower
                    or "out of memory" in stderr_lower
                ):
                    message = f"Memory Limit Exceeded on test: {test_case_number}"
                    add_testcase_result(
                        testcase_results,
                        test_case_number,
                        test_case,
                        SubmissionStatus.MEMORY_LIMIT_EXCEEDED.value,
                        cpu_time,
                        memory_mb,
                    )
                    finish_submission(
                        session,
                        submission_id,
                        SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
                        message,
                        execution_time=current_execution_time,
                        execution_memory=problem.memory_limit,
                    )
                    return runner_response(message, testcase_results, include_testcase_results)
                #  maybe MLE, but conflicts with RE => say RE
                message = f"Runtime Error on test: {test_case_number}"
                add_testcase_result(
                    testcase_results,
                    test_case_number,
                    test_case,
                    SubmissionStatus.RUNTIME_ERROR.value,
                    cpu_time,
                    memory_mb,
                )
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.RUNTIME_ERROR,
                    message,
                    execution_time=current_execution_time,
                    execution_memory=current_memory_usage,
                )
                return runner_response(message, testcase_results, include_testcase_results)
            # measure execution time and memory usage
            memory_usage = current_memory_usage
            execution_time = current_execution_time

            if memory_usage > problem.memory_limit:
                message = f"Memory Limit Exceeded on test: {test_case_number}"
                add_testcase_result(
                    testcase_results,
                    test_case_number,
                    test_case,
                    SubmissionStatus.MEMORY_LIMIT_EXCEEDED.value,
                    cpu_time,
                    memory_mb,
                )
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
                    message,
                    execution_time=execution_time,
                    execution_memory=problem.memory_limit,
                )
                return runner_response(message, testcase_results, include_testcase_results)

            # check time limit exceeded again
            if execution_time > problem.time_limit:
                message = f"Time Limit Exceeded on test: {test_case_number}"
                add_testcase_result(
                    testcase_results,
                    test_case_number,
                    test_case,
                    SubmissionStatus.TIME_LIMIT_EXCEEDED.value,
                    cpu_time,
                    memory_mb,
                )
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.TIME_LIMIT_EXCEEDED,
                    message,
                    execution_time=problem.time_limit,
                    execution_memory=memory_usage,
                )
                return runner_response(message, testcase_results, include_testcase_results)
            # todo : use checker_code and handle exceptions instead of manually checking return output and expected output
            # todo : set test_case number for test_case

            # compare output with expected output
            stdout = process.stdout.read()
            if stdout.strip() != test_case.expected_output.strip():
                message = f"Wrong Answer on test: {test_case_number}"
                add_testcase_result(
                    testcase_results,
                    test_case_number,
                    test_case,
                    SubmissionStatus.WRONG_ANSWER.value,
                    cpu_time,
                    memory_mb,
                )
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.WRONG_ANSWER,
                    message,
                    execution_time=execution_time,
                    execution_memory=memory_usage,
                )
                return runner_response(message, testcase_results, include_testcase_results)
            add_testcase_result(
                testcase_results,
                test_case_number,
                test_case,
                "passed",
                cpu_time,
                memory_mb,
            )

        # if all test cases pass, update submission verdict to "accepted"
        message = "Accepted"
        finish_submission(
            session,
            submission_id,
            SubmissionStatus.ACCEPTED,
            message,
            execution_time=execution_time,
            execution_memory=memory_usage,
        )
        return runner_response(message, testcase_results, include_testcase_results)
       

if __name__ == "__main__":
    run_worker()
