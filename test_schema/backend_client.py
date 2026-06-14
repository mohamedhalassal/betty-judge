import os
import requests
from dotenv import load_dotenv

from models.problem import Problem
from models.test_case import TestCase

load_dotenv()


def backend_url() -> str:
    base_url = os.getenv("BACKEND_URL")
    if not base_url:
        raise RuntimeError(
            "BACKEND_URL is not set. Pass --backend-url or set BACKEND_URL."
        )
    return base_url.rstrip("/")


def auth_headers() -> dict[str, str]:
    token = os.getenv("BACKEND_USER_TOKEN")
    if not token:
        raise RuntimeError(
            "BACKEND_USER_TOKEN is not set. Pass --backend-user-token or set "
            "BACKEND_USER_TOKEN."
        )
    return {"Authorization": f"Bearer {token}"}


def create_problem(problem: Problem, test_cases: list[TestCase]):
    response = requests.post(
        f"{backend_url()}/problems",
        json={
            "name": problem.name,
            "statement": problem.statement,
            "solution": problem.solution,
            "checker_code": problem.checker_code,
            "time_limit": problem.time_limit,
            "memory_limit": problem.memory_limit,
        },
        headers=auth_headers(),
        timeout=30,
    )


    response.raise_for_status()
    problem_id = response.json()["id"]
    for test_case in test_cases:
        response = requests.post(
            f"{BASE_URL}/test_cases/problem/{problem_id}",
            json={
                "input_data": test_case.input_data,
                "expected_output": test_case.expected_output,
                "is_sample": test_case.is_sample,
            },
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()

    return problem_id


def create_submission(problem_id: int, source_code: str):
    response = requests.post(
        f"{backend_url()}/submit",
        json={
            "problem_id": problem_id,
            "source_code": source_code,
        },
        headers=auth_headers(),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_submission(submission_id: int):
    response = requests.get(
        f"{backend_url()}/my-submissions/{submission_id}",
        headers=auth_headers(),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
