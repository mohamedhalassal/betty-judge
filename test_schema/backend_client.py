import os
import requests

BASE_URL = os.getenv("BACKEND_URL")
TOKEN = os.getenv("BACKEND_USER_TOKEN")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def create_problem(problem):
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

    return response.json()


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
