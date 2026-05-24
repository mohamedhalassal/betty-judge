import hashlib
import os
import random
import string
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated
import requests
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from src.database import SessionDep
from src.models.problem import Problem
from src.models.test_case import TestCase
from src.models.user import User


BASE_URL = "https://polygon.codeforces.com/api/"

router = APIRouter()


class PolygonProblemImport(BaseModel):
    polygon_problem_id: int
    testset: str = Field(default="tests")
    test_offset: int = Field(default=0, ge=0)
    max_tests: int | None = Field(default=None, ge=1)
    request_timeout: int = Field(default=15, ge=1, le=120)
    max_workers: int = Field(default=4, ge=1, le=10)
    max_input_bytes: int | None = Field(default=None, ge=1)


def get_polygon_credentials() -> tuple[str, str]:
    api_key = os.environ.get("POLYGON_API_KEY")
    api_secret = os.environ.get("POLYGON_API_SECRET")
    if not api_key or not api_secret:
        raise HTTPException(
            status_code=500,
            detail=(
                "configure POLYGON_API_KEY and POLYGON_API_SECRET"
            ),
        )
    return api_key, api_secret


def make_api_url(method: str, params: dict, api_key: str, api_secret: str) -> str:
    params = params.copy()
    params["apiKey"] = api_key
    params["time"] = int(time.time())

    param_string = "&".join(
        f"{key}={urllib.parse.quote(str(params[key]), safe='')}"
        for key in sorted(params)
    )

    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    to_hash = f"{rand}/{method}?{param_string}#{api_secret}"
    api_sig = rand + hashlib.sha512(to_hash.encode()).hexdigest()

    return f"{BASE_URL}{method}?{param_string}&apiSig={api_sig}"


def call_polygon_json(
    method: str,
    params: dict,
    api_key: str,
    api_secret: str,
    request_timeout: int,
):
    url = make_api_url(method, params, api_key, api_secret)
    try:
        response = requests.get(url, timeout=request_timeout)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Polygon request failed: {exc}")

    if data.get("status") != "OK":
        raise HTTPException(status_code=502, detail={"polygon_error": data})

    return data["result"]


def call_polygon_text(
    method: str,
    params: dict,
    api_key: str,
    api_secret: str,
    request_timeout: int,
) -> str:
    url = make_api_url(method, params, api_key, api_secret)
    try:
        response = requests.get(url, timeout=request_timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Polygon request failed: {exc}")

    return response.text


def fetch_polygon_test_cases(
    polygon_problem_id: int,
    testset: str,
    api_key: str,
    api_secret: str,
    test_offset: int,
    max_tests: int | None,
    request_timeout: int,
    max_workers: int,
    max_input_bytes: int | None,
) -> list[dict]:
    tests = call_polygon_json(
        "problem.tests",
        {"problemId": polygon_problem_id, "testset": testset},
        api_key,
        api_secret,
        request_timeout,
    )

    tests = tests[test_offset:]

    if max_tests is not None:
        tests = tests[:max_tests]

    def fetch_one_test(test: dict):
        test_index = test["index"]
        params = {
            "problemId": polygon_problem_id,
            "testset": testset,
            "testIndex": test_index,
        }
        input_data = call_polygon_text(
            "problem.testInput",
            params,
            api_key,
            api_secret,
            request_timeout,
        )
        if max_input_bytes is not None and len(input_data.encode()) > max_input_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Test {test_index} input exceeds max_input_bytes",
            )
        expected_output = call_polygon_text(
            "problem.testAnswer",
            params,
            api_key,
            api_secret,
            request_timeout,
        )
        return {
            "input_data": input_data,
            "expected_output": expected_output,
            "is_sample": False,
        }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fetch_one_test, tests))

def test_case_response(test_case: TestCase) -> dict:
    return {
        "id": test_case.id,
        "problem_id": test_case.problem_id,
        "is_sample": test_case.is_sample,
    }


@router.post("/polygon/problems", status_code=201)
def create_problem_from_polygon(
    payload: Annotated[PolygonProblemImport, Body(embed=False)],
    session: SessionDep,
):
    api_key, api_secret = get_polygon_credentials()
    polygon_test_cases = fetch_polygon_test_cases(
        payload.polygon_problem_id,
        payload.testset,
        api_key,
        api_secret,
        payload.test_offset,
        payload.max_tests,
        payload.request_timeout,
        payload.max_workers,
        payload.max_input_bytes,
    )

    if not polygon_test_cases:
        raise HTTPException(status_code=400, detail="Polygon problem has no test cases")

    problem = Problem(
        name=f"Polygon {payload.polygon_problem_id}",
        statement=f"Imported from Polygon problem {payload.polygon_problem_id}",
        created_by=4,
        solution=None,
        checker_code=None,
        time_limit=2000,
        memory_limit=256,
    )
    session.add(problem)
    session.commit()
    session.refresh(problem)

    test_cases = []
    for test_case in polygon_test_cases:
        test_case_db = TestCase(
            problem_id=problem.id,
            input_data=test_case["input_data"],
            expected_output=test_case["expected_output"],
            is_sample=test_case["is_sample"],
        )
        try:
            session.add(test_case_db)
            session.commit()
            session.refresh(test_case_db)
        except SQLAlchemyError as exc:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Stored problem {problem.id}, but failed after "
                    f"{len(test_cases)} test cases: {exc}"
                ),
            )
        test_cases.append(test_case_db)
        print(
            f"Inserted Polygon test case {len(test_cases)}/{len(polygon_test_cases)} "
            f"for problem {problem.id}",
            flush=True,
        )

    return {
        "problem": {
            "id": problem.id,
            "name": problem.name,
            "statement": problem.statement,
            "created_by": problem.created_by,
            "solution": problem.solution,
            "checker_code": problem.checker_code,
            "time_limit": problem.time_limit,
            "memory_limit": problem.memory_limit,
        },
        "test_cases_count": len(test_cases),
        "test_cases": [test_case_response(test_case) for test_case in test_cases],
    }
