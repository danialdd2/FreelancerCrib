
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Project

from app.auth import bcrypt_context
from app.main import app
from app.database import Base, get_db

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db



@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client():          
    return TestClient(app)


@pytest.fixture
def db_session(db):
    return db


@pytest.fixture
def client_user(db):

    user = User(
        username="client",
        email="client@test.com",
        full_name="Client",
        hashed_password=bcrypt_context.hash("12345678"),
        user_role="client"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def freelancer(db):

    user = User(
        username="freelancer",
        email="free@test.com",
        full_name="Free",
        hashed_password=bcrypt_context.hash("12345678"),
        user_role="freelancer"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def client_token_headers(test_client, client_user):

    response = test_client.post(
        "/auth/token",
        data={
            "username": "client",
            "password": "12345678"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def freelancer_token_headers(test_client, freelancer):

    response = test_client.post(
        "/auth/token",
        data={
            "username": "freelancer",
            "password": "12345678"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def project(db, client_user):

    project = Project(
        title="Test Project",
        description="Test",
        budget=1000,
        owner_id=client_user.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project