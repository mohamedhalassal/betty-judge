from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
from src.models import test_case
from src.core.security import verify_access_token
from main import app
from src.database import get_session
from src.models.user import User
from src.models.problem import Problem
from src.schemas.problem import ProblemCreate
from src.models.test_case import TestCase
from src.schemas.test_case import TestCaseCreate


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    with Session(engine) as session:    
        yield session

client = TestClient(app)

def setup_function():
    SQLModel.metadata.create_all(engine)
    app.dependency_overrides[get_session] = get_test_session

def teardown_function():
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
def create_test_user(session):
    user = User(
        username="testuser",
        email="test@example.com",
        google_id="google-123",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_problem(session, user, name="Two Sum"):
    problem = Problem(
        name=name,
        statement="Sample statement",
        created_by=user.id,
        solution="Sample solution",
        checker_code="Sample checker code",
    )
    session.add(problem)
    session.commit()
    session.refresh(problem)
    return problem


def create_test_case(session, problem, input_data="Sample input", expected_output="Sample output", is_sample=False):
    test_case = TestCase(
        input_data=input_data,
        expected_output=expected_output,
        is_sample=is_sample,
        problem_id=problem.id
    )
    session.add(test_case)
    session.commit()
    session.refresh(test_case)
    return test_case


def test_get_and_create_test_cases():
     app.dependency_overrides[verify_access_token] = lambda: 1
     with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = TestCaseCreate(
            input_data="input 1",
            expected_output="output 1",
            is_sample=False)

        create_response = client.post(f"/test_cases?problem_id={problem_id}", json=test_case.model_dump())
        assert create_response.status_code == 201


        test_case = TestCaseCreate(
            input_data="input 2",
            expected_output="output 2",
            is_sample=False)

        create_response = client.post(f"/test_cases?problem_id={problem_id}", json=test_case.model_dump())
        assert create_response.status_code == 201

        response = client.get("/test_cases")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["input_data"] == "input 1"
        assert data[1]["input_data"] == "input 2"

def test_delete_test_case():
    app.dependency_overrides[verify_access_token] = lambda: 1

    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem)

    response = client.delete(f"/test_cases/{test_case.id}")

    assert response.status_code == 204
    with Session(engine) as session:
        assert session.exec(select(TestCase).where(TestCase.id == test_case.id)).first() is None

def test_update_test_case():
    app.dependency_overrides[verify_access_token] = lambda: 1

    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem)

    response = client.patch(
        f"/test_cases/{test_case.id}",
        json={
            "input_data": "Updated input",
            "expected_output": "Updated output",
            "is_sample": True
        },
    )

    assert response.status_code == 200
    assert response.json()["input_data"] == "Updated input"
    assert response.json()["expected_output"] == "Updated output"
    assert response.json()["is_sample"] == True

