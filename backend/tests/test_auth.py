from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

from main import app
from src.database import get_session
from src.api.auth import get_google_token_verifier
from src.models.user import User


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    with Session(engine) as session:
        yield session


def fake_valid_google_token(token: str):
    return {
        "google_id": "google-123",
        "email": "test@example.com",
    }


def fake_invalid_google_token(token: str):
    return None


client = TestClient(app)


def setup_function():
    SQLModel.metadata.create_all(engine)
    app.dependency_overrides[get_session] = get_test_session


def teardown_function():
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)

def test_login_invalid_google_token():
    app.dependency_overrides[get_google_token_verifier] = (
        lambda: fake_invalid_google_token
    )

    response = client.post(
        "/login?username=abdosaad",
        json={"token": "bad-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Google token"

def test_login_creates_user():
    app.dependency_overrides[get_google_token_verifier] = (
        lambda: fake_valid_google_token
    )

    response = client.post(
        "/login?username=abdosaad",
        json={"token": "fake-token"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.google_id == "google-123")
        ).first()

        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "abdosaad"

def test_login_existing_user():
    app.dependency_overrides[get_google_token_verifier] = (
        lambda: fake_valid_google_token
    )

    with Session(engine) as session:
        user = User(
            username="abdosaad",
            email="test@example.com",
            google_id="google-123",
        )
        session.add(user)
        session.commit()

    response = client.post(
        "/login?username=abdosaad",
        json={"token": "fake-token"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()
