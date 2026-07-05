from .utils import create_user, login


def test_create_user(test_client):

    response = test_client.post(
        "/user/",
        json={
            "username": "ali",
            "email": "ali@test.com",
            "full_name": "Ali",
            "password": "123456789",
            "user_role": "client"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"


def test_get_me(test_client, db):

    create_user(
        db=db,
        username="ali",
        email="ali@test.com"
    )

    headers = login(test_client, "ali")

    response = test_client.get(
        "/user/me",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "ali"
    assert data["email"] == "ali@test.com"


def test_update_me(test_client, db):

    create_user(
        db=db,
        username="ali",
        email="ali@test.com"
    )

    headers = login(test_client, "ali")

    response = test_client.put(
        "/user/me",
        headers=headers,
        json={
            "username": "newali",
            "email": "new@test.com",
            "full_name": "Ali New"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"


def test_get_other_user(test_client, db):

    create_user(
        db=db,
        username="ali",
        email="ali@test.com"
    )

    create_user(
        db=db,
        username="reza",
        email="reza@test.com"
    )

    headers = login(test_client, "ali")

    response = test_client.get(
        "/user/2",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "reza"