from app.auth import create_access_token
from datetime import timedelta

from .utils import create_user


def test_login_success(test_client, db):
    create_user(
        db=db,
        username="ali",
        email="ali@test.com",
        password="123456789"
    )

    response = test_client.post(
        "/auth/token",
        data={
            "username": "ali",
            "password": "123456789"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(test_client, db):
    create_user(
        db=db,
        username="ali",
        email="ali@test.com",
        password="123456789"
    )

    response = test_client.post(
        "/auth/token",
        data={
            "username": "ali",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_invalid_token(test_client):
    response = test_client.get(
        "/user/me",
        headers={
            "Authorization": "Bearer invalidtoken"
        }
    )

    assert response.status_code == 401


def test_expired_token(test_client, db):
    user = create_user(
        db=db,
        username="ali",
        email="ali@test.com",
        password="123456789"
    )

    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        user_role=user.user_role,
        expires_delta=timedelta(seconds=-1)
    )

    response = test_client.get(
        "/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401