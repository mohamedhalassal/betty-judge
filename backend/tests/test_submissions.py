from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from main import app
from sqlmodel.pool import StaticPool
from src.database import get_session
from src.models.user import User
from src.models.problem import Problem
from src.models.submission import Submission
from src.core.security import verify_access_token,get_current_user


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
    app.dependency_overrides[verify_access_token] = lambda: 1


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
    session.expunge(user)
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
    session.expunge(problem)
    return problem


def create_test_submission(session, user, problem, code="print('hello')"):
    submission = Submission(
        source_code=code,
        problem_id=problem.id,
        user_id=user.id,
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)
    session.expunge(submission)
    return submission


def test_create_and_get_my_submissions():

    with Session(engine) as session:

        user1 = create_test_user(session)

        user2 = User(
            username="anotheruser",
            email="another@example.com",
            google_id="google-456",
        )

        session.add(user2)
        session.commit()
        session.refresh(user2)

        problem = create_test_problem(session, user1)

        create_test_submission(
            session,
            user1,
            problem,
            code="print('user1')"
        )

        create_test_submission(
            session,
            user2,
            problem,
            code="print('user2')"
        )

    app.dependency_overrides[get_current_user] = lambda: user1

    response = client.get("/my-submissions")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["user_id"] == user1.id

    assert data[0]["source_code"] == "print('user1')"


def test_create_submission():

    with Session(engine) as session:

        user = create_test_user(session)

        problem = create_test_problem(session, user)
    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post(
        "/submit",
        json={
            "problem_id": problem.id,
            "source_code": "print(123)"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["problem_id"] == problem.id

    assert data["source_code"] == "print(123)"

    assert data["user_id"] == user.id


def test_get_single_submission():

    with Session(engine) as session:

        user = create_test_user(session)

        problem = create_test_problem(session, user)

        submission = create_test_submission(
            session,
            user,
            problem
        )

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get(f"/my-submissions/{submission.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == submission.id