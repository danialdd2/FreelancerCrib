from ..models import User
from ..auth import bcrypt_context


def create_user(
    db,
    username,
    email,
    password="123456789",
    full_name="Test User",
    role="user",
    user_role="client",
):

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=bcrypt_context.hash(password),
        role=role,
        user_role=user_role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login(test_client, username, password="123456789"):

    response = test_client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def create_project(test_client, headers):

    response = test_client.post(
        "/projects",
        headers=headers,
        json={
            "title": "Test Project",
            "description": "Project Description",
            "budget": 1000,
        },
    )

    assert response.status_code == 201


def create_bid(test_client, headers, project_id):

    response = test_client.post(
        f"/projects/{project_id}/bids",
        headers=headers,
        json={
            "price": 800,
            "message": "I can do it",
        },
    )

    return response


def update_bid(test_client, headers, bid_id):

    return test_client.put(
        f"/bids/{bid_id}",
        headers=headers,
        json={
            "price": 900,
            "message": "Updated",
        },
    )


def create_rating(test_client, headers, project_id):

    return test_client.post(
        f"/projects/{project_id}/ratings",
        headers=headers,
        json={
            "score": 10,
            "comment": "Excellent",
        },
    )
