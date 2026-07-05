from .utils import create_user, login
from ..models import Project
from ..models import Bid
from ..enums import ProjectStatus, BidStatus

def test_create_project(test_client, db):

    create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    headers = login(test_client, "client")

    response = test_client.post(
        "/projects/",
        headers=headers,
        json={
            "title": "Website",
            "description": "Build website",
            "budget": 2000
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Project created successfully."


def test_get_projects(test_client, db):

    owner = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    db.add(Project(
        title="Project One",
        description="Description",
        budget=1000,
        owner_id=owner.id
    ))

    db.add(Project(
        title="Project Two",
        description="Description",
        budget=2000,
        owner_id=owner.id
    ))

    db.commit()

    response = test_client.get("/projects")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_project(test_client, db):

    owner = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    db.add(Project(
        title="Python API",
        description="FastAPI",
        budget=1000,
        owner_id=owner.id
    ))

    db.add(Project(
        title="React Website",
        description="React",
        budget=3000,
        owner_id=owner.id
    ))

    db.commit()

    response = test_client.get("/projects?search=Python")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Python API"


def test_pagination(test_client, db):

    owner = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    for i in range(15):
        db.add(Project(
            title=f"Project {i}",
            description="Test",
            budget=1000,
            owner_id=owner.id
        ))

    db.commit()

    response = test_client.get("/projects?skip=0&limit=10")

    assert response.status_code == 200
    assert len(response.json()) == 10


def test_update_project(test_client, db):

    owner = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    project = Project(
        title="Old Title",
        description="Old",
        budget=1000,
        owner_id=owner.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    headers = login(test_client, "client")

    response = test_client.put(
        f"/projects/{project.id}",
        headers=headers,
        json={
            "title": "New Title",
            "description": "Updated",
            "budget": 5000
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Project updated successfully."

    db.refresh(project)

    assert project.title == "New Title"
    assert project.description == "Updated"
    assert project.budget == 5000


def test_get_my_projects(test_client, db):

    owner = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    db.add(Project(
        title="First",
        description="Test",
        budget=1000,
        owner_id=owner.id
    ))

    db.add(Project(
        title="Second",
        description="Test",
        budget=2000,
        owner_id=owner.id
    ))

    db.commit()

    headers = login(test_client, "client")

    response = test_client.get(
        "/projects/my",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_project_by_id(test_client, db):

    owner = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    project = Project(
        title="My Project",
        description="Description",
        budget=5000,
        owner_id=owner.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    headers = login(test_client, "client")

    response = test_client.get(
        f"/projects/{project.id}",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project.id
    assert data["title"] == "My Project"




def test_accept_bid(test_client, db):

    client_user = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    freelancer = create_user(
        db=db,
        username="freelancer",
        email="freelancer@test.com",
        user_role="freelancer"
    )

    project = Project(
        title="Project",
        description="Desc",
        budget=1000,
        owner_id=client_user.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    bid = Bid(
        price=900,
        message="I'll do it",
        project_id=project.id,
        freelancer_id=freelancer.id
    )

    db.add(bid)
    db.commit()
    db.refresh(bid)

    headers = login(test_client, "client")

    response = test_client.patch(
        f"/projects/{project.id}/bids/{bid.id}/accept",
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Bid accepted successfully."

    db.refresh(project)
    db.refresh(bid)

    assert project.status == ProjectStatus.IN_PROGRESS
    assert bid.status == BidStatus.ACCEPTED
    assert project.winner_id == freelancer.id


def test_accept_second_bid(test_client, db):

    client_user = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    freelancer = create_user(
        db=db,
        username="freelancer",
        email="freelancer@test.com",
        user_role="freelancer"
    )

    project = Project(
        title="Project",
        description="Desc",
        budget=1000,
        owner_id=client_user.id,
        status=ProjectStatus.IN_PROGRESS
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    bid = Bid(
        price=900,
        message="I'll do it",
        project_id=project.id,
        freelancer_id=freelancer.id
    )

    db.add(bid)
    db.commit()
    db.refresh(bid)

    headers = login(test_client, "client")

    response = test_client.patch(
        f"/projects/{project.id}/bids/{bid.id}/accept",
        headers=headers
    )

    assert response.status_code == 400


def test_complete_project(test_client, db):

    client_user = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    freelancer = create_user(
        db=db,
        username="freelancer",
        email="freelancer@test.com",
        user_role="freelancer"
    )

    project = Project(
        title="Project",
        description="Desc",
        budget=1000,
        owner_id=client_user.id,
        winner_id=freelancer.id,
        status=ProjectStatus.IN_PROGRESS
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    headers = login(test_client, "client")

    response = test_client.patch(
        f"/projects/projects/{project.id}/complete",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Project completed successfully."

    db.refresh(project)

    assert project.status == ProjectStatus.COMPLETED


def test_complete_again(test_client, db):

    client_user = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    freelancer = create_user(
        db=db,
        username="freelancer",
        email="freelancer@test.com",
        user_role="freelancer"
    )

    project = Project(
        title="Project",
        description="Desc",
        budget=1000,
        owner_id=client_user.id,
        winner_id=freelancer.id,
        status=ProjectStatus.COMPLETED
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    headers = login(test_client, "client")

    response = test_client.patch(
        f"/projects/projects/{project.id}/complete",
        headers=headers
    )

    assert response.status_code == 400


def test_cancel_project(test_client, db):

    client_user = create_user(
        db=db,
        username="client",
        email="client@test.com",
        user_role="client"
    )

    project = Project(
        title="Project",
        description="Desc",
        budget=1000,
        owner_id=client_user.id,
        status=ProjectStatus.OPEN
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    headers = login(test_client, "client")

    response = test_client.patch(
        f"/projects/projects/{project.id}/cancel",
        headers=headers
    )

    assert response.status_code == 200

    db.refresh(project)

    assert project.status == ProjectStatus.CANCELED