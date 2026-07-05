from ..models import Notification
from ..enums import NotificationType


def create_notification(db_session, client_user):
    notification = Notification(
        user_id=client_user.id,
        title="Test",
        message="Hello",
        type=NotificationType.NEW_BID
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification


def test_get_notifications(test_client, db_session, client_user, client_token_headers):
    create_notification(db_session, client_user)

    response = test_client.get(
        "/notifications/",
        headers=client_token_headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_unread_notifications(test_client, db_session, client_user, client_token_headers):
    create_notification(db_session, client_user)

    response = test_client.get(
        "/notifications/unread",
        headers=client_token_headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_notification(test_client, db_session, client_user, client_token_headers):
    notification = create_notification(db_session, client_user)

    response = test_client.patch(
        f"/notifications/{notification.id}/read",
        headers=client_token_headers
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_read_all_notifications(test_client, db_session, client_user, client_token_headers):
    create_notification(db_session, client_user)
    create_notification(db_session, client_user)

    response = test_client.patch(
        "/notifications/read-all",
        headers=client_token_headers
    )

    assert response.status_code == 200


def test_delete_notification(test_client, db_session, client_user, client_token_headers):
    notification = create_notification(db_session, client_user)

    response = test_client.delete(
        f"/notifications/{notification.id}",
        headers=client_token_headers
    )

    assert response.status_code == 200


def test_unread_count(test_client, db_session, client_user, client_token_headers):
    create_notification(db_session, client_user)
    create_notification(db_session, client_user)

    response = test_client.get(
        "/notifications/unread-count",
        headers=client_token_headers
    )

    assert response.status_code == 200
    assert response.json() == 2