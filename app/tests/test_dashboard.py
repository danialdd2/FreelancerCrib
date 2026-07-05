from ..models import Bid
from ..enums import ProjectStatus


def test_client_dashboard(
    test_client,
    db_session,
    client_user,
    client_token_headers,
    project
):
    response = test_client.get(
        "/dashboard/",
        headers=client_token_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "projects_created" in data
    assert "projects_completed" in data
    assert "client_open_projects" in data
    assert "active_projects" in data
    assert "total_bids" in data
    assert "rating" in data


def test_freelancer_dashboard(
    test_client,
    db_session,
    freelancer_token_headers
):
    response = test_client.get(
        "/dashboard/",
        headers=freelancer_token_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "bids_sent" in data
    assert "pending_bids" in data
    assert "projects_won" in data
    assert "projects_completed" in data
    assert "active_projects" in data
    assert "rating" in data