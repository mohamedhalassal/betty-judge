import os
import requests
from dotenv import load_dotenv

from models.problem import Problem
from models.test_case import TestCase

load_dotenv()

BASE_URL = os.getenv("BACKEND_URL")
TOKEN = os.getenv("BACKEND_USER_TOKEN")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def create_problem(problem: Problem, test_cases: list[TestCase]):
    response = requests.post(
        f"{BASE_URL}/problems",
        json={
            "name": problem.name,
            "statement": problem.statement,
            "solution": problem.solution,
            "checker_code": problem.checker_code,
            "time_limit": problem.time_limit,
            "memory_limit": problem.memory_limit,
        },
        headers=HEADERS,
        timeout=30,
    )


    response.raise_for_status()
    problem_id = response.json()["id"]
    for test_case in test_cases:
        response = requests.post(
            f"{BASE_URL}/test_cases?problem_id={problem_id}",
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
        f"{BASE_URL}/submit",
        json={
            "problem_id": problem_id,
            "source_code": source_code,
        },
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
