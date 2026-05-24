import subprocess
import tempfile
import resource
import math
import signal
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Annotated
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

REPO_DIR = Path(__file__).resolve().parents[2]
load_dotenv(REPO_DIR / "backend" / ".env")
sys.path.insert(0, str(REPO_DIR / "judge"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in backend/.env")
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'").replace("\\&", "&")
engine = create_engine(DATABASE_URL)


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


@router.post("/runner", status_code=201)
def judge_submission(session: SessionDep, submission_id: int):
    submission, problem = validation(session, submission_id)

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
                message
            )
            return message
        # get test cases for the problem
        test_cases = session.exec(
            select(TestCase).where(TestCase.problem_id == submission.problem_id)
        ).all()
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

        for test_case in test_cases:
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

            if wall_timed_out:
                message = f"Idleness Limit Exceeded on test: {test_case.id}"
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.IDLENESS_LIMIT_EXCEEDED,
                    message,
                )
                return message  
            # time limit exceeded and runtime error and memory limit exceeded cases after signal
            if process.returncode != 0:
                sig = -process.returncode
                # time limit exceeded case
                if sig == signal.SIGXCPU or (
                    sig == signal.SIGKILL
                    and usage.ru_utime + usage.ru_stime >= cpu_limit_seconds
                ):
                    message = f"Time Limit Exceeded on test: {test_case.id}"
                    finish_submission(
                        session,
                        submission_id,
                        SubmissionStatus.TIME_LIMIT_EXCEEDED,
                        message,
                    )
                    return message
                stderr_lower = process.stderr.read().lower()

                #  clear MLE cases
                if (
                    "bad_alloc" in stderr_lower
                    or "cannot allocate memory" in stderr_lower
                    or "out of memory" in stderr_lower
                ):
                    message = f"Memory Limit Exceeded on test: {test_case.id}"
                    finish_submission(
                        session,
                        submission_id,
                        SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
                        message,
                    )
                    return message
                #  maybe MLE, but conflicts with RE => say RE
                message = f"Runtime Error on test: {test_case.id}"
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.RUNTIME_ERROR,
                    message,
                )
                return message
            # measure execution time and memory usage
            cpu_time = (usage.ru_utime + usage.ru_stime) * 1000
            memory_kb = usage.ru_maxrss / 1024.0  # to be in MB
            memory_usage = max(memory_usage, memory_kb)
            execution_time = max(execution_time, cpu_time)

            # check time limit exceeded again
            if execution_time > problem.time_limit:
                message = f"Time Limit Exceeded on test: {test_case.id}"
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.TIME_LIMIT_EXCEEDED,
                    message,
                )
                return message
            # check memory limit exceeded again
            if memory_usage > problem.memory_limit:
                message = f"Memory Limit Exceeded on test: {test_case.id}"
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
                    message,
                )
                return message
            # todo : use checker_code and handle exceptions instead of manually checking return output and expected output
            # todo : set test_case number for test_case

            # compare output with expected output
            stdout = process.stdout.read()
            if stdout.strip() != test_case.expected_output.strip():
                message = f"Wrong Answer on test: {test_case.id}"
                finish_submission(
                    session,
                    submission_id,
                    SubmissionStatus.WRONG_ANSWER,
                    message,
                )
                return message

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
        return message
       
