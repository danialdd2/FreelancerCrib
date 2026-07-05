from ..models import Bid


def test_create_bid(test_client, freelancer_token_headers, project):
    response = test_client.post(
        f"/projects/{project.id}/bids",
        headers=freelancer_token_headers,
        json={
            "price": 500,
            "message": "I can do it"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Bid submitted successfully"


def test_duplicate_bid(test_client, freelancer_token_headers, project):
    test_client.post(
        f"/projects/{project.id}/bids",
        headers=freelancer_token_headers,
        json={
            "price": 500,
            "message": "first"
        }
    )

    response = test_client.post(
        f"/projects/{project.id}/bids",
        headers=freelancer_token_headers,
        json={
            "price": 600,
            "message": "second"
        }
    )

    assert response.status_code == 400


def test_owner_cannot_bid(test_client, client_token_headers, project):
    response = test_client.post(
        f"/projects/{project.id}/bids",
        headers=client_token_headers,
        json={
            "price": 500,
            "message": "owner"
        }
    )

    assert response.status_code == 403


def test_my_bids(test_client, freelancer_token_headers, project):
    test_client.post(
        f"/projects/{project.id}/bids",
        headers=freelancer_token_headers,
        json={
            "price": 500,
            "message": "hello"
        }
    )

    response = test_client.get(
        "/users/me/bids",
        headers=freelancer_token_headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_bid(test_client, db_session, freelancer_token_headers, freelancer, project):
    bid = Bid(
        price=300,
        message="old",
        freelancer_id=freelancer.id,
        project_id=project.id
    )

    db_session.add(bid)
    db_session.commit()

    response = test_client.put(
        f"/bids/{bid.id}",
        headers=freelancer_token_headers,
        json={
            "price": 800,
            "message": "updated"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Bid updated successfully"


def test_delete_bid(test_client, db_session, freelancer_token_headers, freelancer, project):
    bid = Bid(
        price=500,
        message="delete me",
        freelancer_id=freelancer.id,
        project_id=project.id
    )

    db_session.add(bid)
    db_session.commit()

    response = test_client.delete(
        f"/bids/{bid.id}",
        headers=freelancer_token_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Bid deleted successfully"