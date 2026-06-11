import signal
from dataclasses import dataclass

from src.models.submission import SubmissionStatus


def verdict_value(verdict) -> str:
    if verdict is None:
        return "-"
    return getattr(verdict, "value", str(verdict))


@dataclass
class VerdictResult:
    verdict: SubmissionStatus
    message: str
    execution_time: int
    execution_memory: int


def classify_testcase_result(
    result,
    expected_output: str,
    test_case_number: int,
    problem_time_limit: int,
    problem_memory_limit: int,
    execution_time: int,
    memory_usage: int,
    cpu_limit_seconds: int,
) -> VerdictResult | None:
    if result.wall_timed_out:
        message = f"Idleness Limit Exceeded on test: {test_case_number}"
        return VerdictResult(
            verdict=SubmissionStatus.IDLENESS_LIMIT_EXCEEDED,
            message=message,
            execution_time=execution_time,
            execution_memory=memory_usage,
        )
    # time limit exceeded case
    sig = -result.returncode
    if result.returncode != 0 and (sig == signal.SIGXCPU or(sig == signal.SIGKILL and result.cpu_time_ms / 1000 >= cpu_limit_seconds)):
            message = f"Time Limit Exceeded on test: {test_case_number}"
            return VerdictResult(
                verdict=SubmissionStatus.TIME_LIMIT_EXCEEDED,
                message=message,
                execution_time=problem_time_limit,
                execution_memory=problem_memory_limit,
            )

    stderr_lower = result.stderr.lower()

    # clear MLE cases
    if result.returncode != 0 and ("bad_alloc" in stderr_lower
        or "cannot allocate memory" in stderr_lower
        or "out of memory" in stderr_lower
    ):
        message = f"Memory Limit Exceeded on test: {test_case_number}"
        return VerdictResult(
            verdict=SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
            message=message,
            execution_time=execution_time,
            execution_memory=problem_memory_limit,
        )

    # maybe MLE, but conflicts with RE => say RE
    if result.returncode != 0:
        message = f"Runtime Error on test: {test_case_number}"
        return VerdictResult(
            verdict=SubmissionStatus.RUNTIME_ERROR,
            message=message,
            execution_time=execution_time,
            execution_memory=memory_usage,
        )

    # measure execution time and memory usage
    if memory_usage > problem_memory_limit:
        message = f"Memory Limit Exceeded on test: {test_case_number}"
        return VerdictResult(
            verdict=SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
            message=message,
            execution_time=execution_time,
            execution_memory=problem_memory_limit,
        )

    # check time limit exceeded again
    if execution_time > problem_time_limit:
        message = f"Time Limit Exceeded on test: {test_case_number}"
        return VerdictResult(
            verdict=SubmissionStatus.TIME_LIMIT_EXCEEDED,
            message=message,
            execution_time=problem_time_limit,
            execution_memory=memory_usage,
        )
 
    # compare output with expected output
    stdout = result.stdout
    if stdout.strip() != expected_output.strip():
        message = f"Wrong Answer on test: {test_case_number}"
        return VerdictResult(
            verdict=SubmissionStatus.WRONG_ANSWER,
            message=message,
            execution_time=execution_time,
            execution_memory=memory_usage,
        )
    return None