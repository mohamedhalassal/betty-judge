from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
from src.core.security import verify_access_token
from main import app
from src.database import get_session
from src.models.user import User
from src.models.problem import Problem
from src.schemas.problem import ProblemCreate


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def fake_verify_access_token():
    return 1
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

    
def test_get_and_create_problems():
     app.dependency_overrides[verify_access_token] = fake_verify_access_token

     with Session(engine) as session:
        user = create_test_user(session)

        user_id = user.id

        problem = ProblemCreate(name="Two Sum", statement="Sample statement",
        solution="Sample solution", #pyright: ignore
        checker_code="Sample checker code")
        
        create_response = client.post("/problems", json=problem.model_dump())
        assert create_response.status_code == 201


        problem = ProblemCreate(name="Playing Football", statement="Sample statement",
        solution="Sample solution", #pyright: ignore
        checker_code="Sample checker code")
        create_response = client.post("/problems", json=problem.model_dump())
        assert create_response.status_code == 201

        response = client.get("/problems")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Two Sum"
        assert data[1]["name"] == "Playing Football"
        assert data[0]["created_by"] == user_id
        assert data[1]["created_by"] == user_id


        response_search = client.get("/problems?search=football")
        assert response_search.status_code == 200
        assert len(response_search.json()) == 1
        assert response_search.json()[0]["name"] == "Playing Football"



def test_delete_problem():
    app.dependency_overrides[verify_access_token] = lambda: 1

    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)

    response = client.delete(f"/problems/{problem.id}")

    assert response.status_code == 200
    with Session(engine) as session:
        assert session.exec(select(Problem).where(Problem.id == problem.id)).first() is None

def test_update_problem():
    app.dependency_overrides[verify_access_token] = lambda: 1

    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)

    response = client.patch(
        f"/problems/{problem.id}",
        json={
            "name": "Updated Problem",
            "statement": "Updated statement",
            "solution": "Updated solution",
            "checker_code": "Updated checker",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Problem"
