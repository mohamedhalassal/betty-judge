import tempfile
import math
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_DIR / "judge"))

from sqlmodel import Session, select
from src.models.test_case import TestCase
from src.models.submission import SubmissionStatus
from src.compiler import compile_cpp
from src.executor import run_testcase
from src.verdict import classify_testcase_result
from src.sandbox import build_resource_limiter
from src.repository import load_submission_for_judging
from src.repository import finish_submission


def judge_submission(
    session: Session,
    submission_id: int,
):
    submission, problem = load_submission_for_judging(session, submission_id)
    if submission is None:
        message = "Submission verdict is not in queue"
        return message

    # compile the code
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        compile_result = compile_cpp(submission.source_code, temp_path)

        # compilation error
        if not compile_result.success:
            message = compile_result.message
            finish_submission(
                session,
                submission_id,
                SubmissionStatus.COMPILE_ERROR,
                message,
                execution_time=0,
                execution_memory=0,
            )
            return message
        exe_file = compile_result.exe_file

        execution_time = 0
        memory_usage = 0

        # run the executable with each test case and compare output
        cpu_limit_seconds = max(1, math.ceil(problem.time_limit / 1000))
        wall_limit_seconds = cpu_limit_seconds * 3 + 5

        limit_resources = build_resource_limiter(cpu_limit_seconds, problem.memory_limit)

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

            result = run_testcase(
                exe_file=exe_file,
                input_data=test_case.input_data,
                limit_resources=limit_resources,
                wall_limit_seconds=wall_limit_seconds,
            )
            current_execution_time = max(execution_time, result.cpu_time_ms)
            current_memory_usage = max(memory_usage, result.memory_mb)
            verdict_result = classify_testcase_result(
                result=result,
                expected_output=test_case.expected_output,
                test_case_number=test_case_number,
                problem_time_limit=problem.time_limit,
                problem_memory_limit=problem.memory_limit,
                current_execution_time=current_execution_time,
                current_memory_usage=current_memory_usage,
                cpu_limit_seconds=cpu_limit_seconds,
            )

            if verdict_result is not None:
                finish_submission(
                    session,
                    submission_id,
                    verdict_result.verdict,
                    verdict_result.message,
                    execution_time=verdict_result.execution_time,
                    execution_memory=verdict_result.execution_memory,
                )
                return verdict_result.message
            execution_time = current_execution_time
            memory_usage = current_memory_usage
            
        
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