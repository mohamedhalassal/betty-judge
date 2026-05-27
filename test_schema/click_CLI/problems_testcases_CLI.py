import hashlib
import os
import random
import string
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
import requests
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from sqlmodel import create_engine, Session, SQLModel

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(BACKEND_DIR))

TEST_SCHEMA_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEST_SCHEMA_DIR))

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)
from models.problem import Problem
from models.test_case import TestCase
from models.user import User


BASE_URL = "https://polygon.codeforces.com/api/"


def get_polygon_credentials() -> tuple[str, str]:
    api_key = os.environ.get("POLYGON_API_KEY")
    api_secret = os.environ.get("POLYGON_API_SECRET")
    if not api_key or not api_secret:
        raise click.ClickException(
            "configure POLYGON_API_KEY and POLYGON_API_SECRET in backend/.env"
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
        raise click.ClickException(f"Polygon request failed: {exc}") from exc

    if data.get("status") != "OK":
        raise click.ClickException(f"Polygon error: {data}")

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
        raise click.ClickException(f"Polygon request failed: {exc}") from exc

    return response.text


def optional_polygon_json(
    method: str,
    params: dict,
    api_key: str,
    api_secret: str,
    request_timeout: int,
):
    try:
        return call_polygon_json(method, params, api_key, api_secret, request_timeout)
    except click.ClickException as exc:
        click.echo(f"Skipping {method}: {exc}", err=True)
        return None


def optional_polygon_text(
    method: str,
    params: dict,
    api_key: str,
    api_secret: str,
    request_timeout: int,
) -> str | None:
    try:
        return call_polygon_text(method, params, api_key, api_secret, request_timeout)
    except click.ClickException as exc:
        click.echo(f"Skipping {method}: {exc}", err=True)
        return None


def get_value(data: dict | None, *names: str):
    if data is None:
        return None
    for name in names:
        if name in data and data[name] is not None:
            return data[name]
    return None


def statement_to_text(statement: dict | None) -> str | None:
    if not statement:
        return None

    parts = []
    for key, title in (
        ("legend", "Statement"),
        ("input", "Input"),
        ("output", "Output"),
        ("scoring", "Scoring"),
        ("notes", "Notes"),
        ("tutorial", "Tutorial"),
    ):
        value = get_value(statement, key, key.capitalize())
        if value:
            parts.append(f"{title}\n{value}")

    return "\n\n".join(parts) if parts else None


def choose_statement(statements: dict | None, statement_lang: str) -> dict | None:
    if not statements:
        return None
    if statement_lang in statements:
        return statements[statement_lang]
    lowered_lang = statement_lang.lower()
    for lang, statement in statements.items():
        if lang.lower() == lowered_lang:
            return statement
    return next(iter(statements.values()), None)


def choose_main_solution(solutions: list[dict] | None) -> dict | None:
    if not solutions:
        return None
    for solution in solutions:
        tag = str(get_value(solution, "tag", "Tag") or "").upper()
        if tag == "MA":
            return solution
    return solutions[0]


def fetch_polygon_problem_attributes(
    polygon_problem_id: int,
    statement_lang: str,
    api_key: str,
    api_secret: str,
    request_timeout: int,
) -> dict:
    params = {"problemId": polygon_problem_id}
    problem_info = optional_polygon_json(
        "problem.info",
        params,
        api_key,
        api_secret,
        request_timeout,
    )
    problems = optional_polygon_json(
        "problems.list",
        {"id": polygon_problem_id},
        api_key,
        api_secret,
        request_timeout,
    )
    statements = optional_polygon_json(
        "problem.statements",
        params,
        api_key,
        api_secret,
        request_timeout,
    )
    checker_name = optional_polygon_text(
        "problem.checker",
        params,
        api_key,
        api_secret,
        request_timeout,
    )
    solutions = optional_polygon_json(
        "problem.solutions",
        params,
        api_key,
        api_secret,
        request_timeout,
    )

    problem_from_list = problems[0] if problems else None
    statement = choose_statement(statements, statement_lang)
    main_solution = choose_main_solution(solutions)
    main_solution_name = get_value(main_solution, "name", "Name")

    solution_code = None
    if main_solution_name:
        solution_code = optional_polygon_text(
            "problem.viewSolution",
            {"problemId": polygon_problem_id, "name": main_solution_name},
            api_key,
            api_secret,
            request_timeout,
        )

    checker_code = None
    if checker_name:
        checker_code = optional_polygon_text(
            "problem.viewFile",
            {
                "problemId": polygon_problem_id,
                "type": "source",
                "name": checker_name.strip(),
            },
            api_key,
            api_secret,
            request_timeout,
        )

    return {
        "name": (
            get_value(statement, "name", "Name")
            or get_value(problem_from_list, "name", "Name")
        ),
        "statement": statement_to_text(statement),
        "solution": solution_code,
        "checker_code": checker_code,
        "time_limit": get_value(problem_info, "timeLimit", "TimeLimit"),
        "memory_limit": get_value(problem_info, "memoryLimit", "MemoryLimit"),
    }


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
            raise click.ClickException(
                f"Test {test_index} input exceeds max_input_bytes"
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


def create_problem_from_polygon(
    session: Session,
    polygon_problem_id: int,
    testset: str,
    test_offset: int,
    max_tests: int | None,
    request_timeout: int,
    max_workers: int,
    max_input_bytes: int | None,
    created_by: int,
    name: str | None,
    statement: str | None,
    statement_lang: str,
    time_limit: int | None,
    memory_limit: int | None,
):
    if session.get(User, created_by) is None:
        raise click.ClickException(f"User {created_by} was not found in the database")

    api_key, api_secret = get_polygon_credentials()
    attributes = fetch_polygon_problem_attributes(
        polygon_problem_id,
        statement_lang,
        api_key,
        api_secret,
        request_timeout,
    )
    polygon_test_cases = fetch_polygon_test_cases(
        polygon_problem_id,
        testset,
        api_key,
        api_secret,
        test_offset,
        max_tests,
        request_timeout,
        max_workers,
        max_input_bytes,
    )

    if not polygon_test_cases:
        raise click.ClickException("Polygon problem has no test cases")

    problem = Problem(
        name=name or attributes["name"] or f"Polygon {polygon_problem_id}",
        statement=(
            statement
            or attributes["statement"]
            or f"Imported from Polygon problem {polygon_problem_id}"
        ),
        created_by=created_by,
        solution=attributes["solution"],
        checker_code=attributes["checker_code"],
        time_limit=time_limit or attributes["time_limit"] or 2000,
        memory_limit=memory_limit or attributes["memory_limit"] or 256,
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
            raise click.ClickException(
                f"Stored problem {problem.id}, but failed after "
                f"{len(test_cases)} test cases: {exc}"
            )
        test_cases.append(test_case_db)
        click.echo(
            f"Inserted Polygon test case {len(test_cases)}/{len(polygon_test_cases)} "
            f"for problem {problem.id}"
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


@click.command()
@click.option(
    "--polygon-problem-id",
    type=int,
    required=True,
    help="Polygon problem ID to import tests from.",
)
@click.option(
    "--testset",
    default="tests",
    show_default=True,
    help="Polygon testset name.",
)
@click.option(
    "--test-offset",
    type=int,
    default=0,
    show_default=True,
    help="Skip this many tests before importing.",
)
@click.option(
    "--max-tests",
    type=int,
    default=None,
    help="Maximum number of tests to import after applying test offset.",
)
@click.option(
    "--request-timeout",
    type=int,
    default=15,
    show_default=True,
    help="Timeout in seconds for each Polygon API request.",
)
@click.option(
    "--max-workers",
    type=int,
    default=4,
    show_default=True,
    help="Number of parallel workers used to download tests.",
)
@click.option(
    "--max-input-bytes",
    type=int,
    default=None,
    help="Reject any test whose input is larger than this many bytes.",
)
@click.option(
    "--created-by",
    type=int,
    default=4,
    show_default=True,
    help="Local user ID that will own the imported problem.",
)
@click.option(
    "--name",
    default=None,
    help="Problem name to store locally. Defaults to 'Polygon <id>'.",
)
@click.option(
    "--statement",
    default=None,
    help="Problem statement to store locally. Defaults to an import note.",
)
@click.option(
    "--statement-lang",
    default="english",
    show_default=True,
    help="Polygon statement language to import.",
)
@click.option(
    "--time-limit",
    type=int,
    default=None,
    help="Override problem time limit in milliseconds. Defaults to Polygon value.",
)
@click.option(
    "--memory-limit",
    type=int,
    default=None,
    help="Override problem memory limit in megabytes. Defaults to Polygon value.",
)
def import_polygon_problem(
    polygon_problem_id,
    testset,
    test_offset,
    max_tests,
    request_timeout,
    max_workers,
    max_input_bytes,
    created_by,
    name,
    statement,
    statement_lang,
    time_limit,
    memory_limit,
):
    with Session(engine) as session:
        result = create_problem_from_polygon(
            session=session,
            polygon_problem_id=polygon_problem_id,
            testset=testset,
            test_offset=test_offset,
            max_tests=max_tests,
            request_timeout=request_timeout,
            max_workers=max_workers,
            max_input_bytes=max_input_bytes,
            created_by=created_by,
            name=name,
            statement=statement,
            statement_lang=statement_lang,
            time_limit=time_limit,
            memory_limit=memory_limit,
        )

    click.echo(
        f"Imported problem {result['problem']['id']} with "
        f"{result['test_cases_count']} test case(s)."
    )


if __name__ == "__main__":
    import_polygon_problem()
