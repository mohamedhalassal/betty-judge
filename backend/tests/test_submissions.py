from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from src.database import get_session
from src.models.user import User
from src.models.problem import Problem
from src.models.submission import Submission, SubmissionStatus
from src.core.security import verify_access_token, get_current_user

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


def create_test_user(session, username="testuser"):
    user = User(
        username=username,
        email=f"{username}@example.com",
        google_id=f"{username}-google-id",
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
        time_limit=2000,
        memory_limit=100
    )

    session.add(problem)
    session.commit()
    session.refresh(problem)
    session.expunge(problem)

    return problem


def create_test_submission(
    session,
    user,
    problem,
    code="print('hello')",
    verdict=SubmissionStatus.IN_QUEUE
):
    submission = Submission(
        source_code=code,
        problem_id=problem.id,
        user_id=user.id,
        verdict=verdict
    )

    session.add(submission)
    session.commit()
    session.refresh(submission)
    session.expunge(submission)

    return submission


def test_create_and_get_my_submissions():

    with Session(engine) as session:

        user1 = create_test_user(session, "user1")
        user2 = create_test_user(session, "user2")

        problem = create_test_problem(session, user1)

        create_test_submission(session, user1, problem, code="print('user1')")

        create_test_submission(session, user2, problem, code="print('user2')")

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

    response = client.post(
        "/submit", json={"problem_id": problem.id, "source_code": "print(123)"}
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

        submission = create_test_submission(session, user, problem)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get(f"/my-submissions/{submission.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == submission.id

    assert data["source_code"] == "print('hello')"


def test_submissions_pagination():

    with Session(engine) as session:

        user = create_test_user(session)

        problem = create_test_problem(session, user)

        for i in range(25):

            create_test_submission(session, user, problem, code=f"print({i})")

    response = client.get("/submissions?page=1&size=10")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 10

    # descending order
    assert data[0]["source_code"] == "print(24)"

    assert data[-1]["source_code"] == "print(15)"


def test_submissions_second_page():

    with Session(engine) as session:

        user = create_test_user(session)

        problem = create_test_problem(session, user)

        for i in range(25):

            create_test_submission(session, user, problem, code=f"print({i})")

    response = client.get("/submissions?page=2&size=10")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 10

    assert data[0]["source_code"] == "print(14)"

    assert data[-1]["source_code"] == "print(5)"


def test_submissions_last_page():

    with Session(engine) as session:

        user = create_test_user(session)

        problem = create_test_problem(session, user)

        for i in range(25):

            create_test_submission(session, user, problem, code=f"print({i})")

    response = client.get("/submissions?page=3&size=10")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 5

    assert data[0]["source_code"] == "print(4)"

    assert data[-1]["source_code"] == "print(0)"


def test_submissions_size_limit():

    response = client.get("/submissions?size=101")

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["loc"] == ["query", "size"]

    assert data["detail"][0]["type"] == "less_than_equal"


def test_submissions_invalid_page():

    response = client.get("/submissions?page=0")

    assert response.status_code == 422


def test_submissions_invalid_size():

    response = client.get("/submissions?size=0")

    assert response.status_code == 422


def test_filter_submissions_by_username():

    with Session(engine) as session:

        user1 = create_test_user(session, "ahmed")
        user2 = create_test_user(session, "mohamed")

        problem = create_test_problem(session, user1)

        create_test_submission(session, user1, problem, code="print('ahmed')")

        create_test_submission(session, user2, problem, code="print('mohamed')")

    response = client.get("/submissions?username=ahmed")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["user_id"] == user1.id

    assert data[0]["source_code"] == "print('ahmed')"


def test_filter_submissions_by_problem():

    with Session(engine) as session:

        user = create_test_user(session)

        problem1 = create_test_problem(session, user, "Two Sum")
        problem2 = create_test_problem(session, user, "Binary Search")

        create_test_submission(session, user, problem1, code="print('problem1')")

        create_test_submission(session, user, problem2, code="print('problem2')")

    response = client.get(f"/submissions?problem_id={problem1.id}")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["problem_id"] == problem1.id

    assert data[0]["source_code"] == "print('problem1')"

def test_filter_submissions_by_verdict():

    with Session(engine) as session:

        user = create_test_user(session)

        problem = create_test_problem(session, user)

        create_test_submission(
            session,
            user,
            problem,
            code="print('AC')",
            verdict=SubmissionStatus.ACCEPTED
        )

        create_test_submission(
            session,
            user,
            problem,
            code="print('WA')",
            verdict=SubmissionStatus.WRONG_ANSWER
        )

    response = client.get("/submissions?verdict=accepted")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["verdict"] == "accepted"

    assert data[0]["source_code"] == "print('AC')"

def test_filter_submissions_by_username_and_verdict():

    with Session(engine) as session:

        user1 = create_test_user(session, "ahmed")
        user2 = create_test_user(session, "mohamed")

        problem = create_test_problem(session, user1)

        create_test_submission(
            session,
            user1,
            problem,
            code="accepted code",
            verdict=SubmissionStatus.ACCEPTED
        )

        create_test_submission(
            session,
            user1,
            problem,
            code="wrong answer code",
            verdict=SubmissionStatus.WRONG_ANSWER
        )

        create_test_submission(
            session,
            user2,
            problem,
            code="another accepted",
            verdict=SubmissionStatus.ACCEPTED
        )

    response = client.get(
        "/submissions?username=ahmed&verdict=accepted"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["source_code"] == "accepted code"

    assert data[0]["verdict"] == "accepted"