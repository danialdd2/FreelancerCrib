from ..models import Rating
from ..enums import ProjectStatus


def prepare_completed_project(db_session, project, freelancer):
    project.status = ProjectStatus.COMPLETED
    project.winner_id = freelancer.id
    db_session.commit()


def test_create_rating(
    test_client,
    db_session,
    project,
    freelancer,
    client_token_headers
):
    prepare_completed_project(db_session, project, freelancer)

    response = test_client.post(
        f"/projects/{project.id}/ratings",
        headers=client_token_headers,
        json={
            "score": 10,
            "comment": "Excellent"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Rating submitted successfully"


def test_duplicate_rating(
    test_client,
    db_session,
    project,
    freelancer,
    client_user,
    client_token_headers
):
    prepare_completed_project(db_session, project, freelancer)

    rating = Rating(
        score=10,
        comment="good",
        project_id=project.id,
        from_user_id=client_user.id,
        to_user_id=freelancer.id
    )

    db_session.add(rating)
    db_session.commit()

    response = test_client.post(
        f"/projects/{project.id}/ratings",
        headers=client_token_headers,
        json={
            "score": 9,
            "comment": "again"
        }
    )

    assert response.status_code == 400


def test_rating_before_completion(
    test_client,
    client_token_headers,
    project
):
    response = test_client.post(
        f"/projects/{project.id}/ratings",
        headers=client_token_headers,
        json={
            "score": 8,
            "comment": "nice"
        }
    )

    assert response.status_code == 400