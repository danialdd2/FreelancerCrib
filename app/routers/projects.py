from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Path
from starlette import status
from ..schemas import CreateProjectRequest,ProjectsResponse
from ..models import Project, Bid, Notification
from sqlalchemy import or_
from ..enums import NotificationType,ProjectStatus,BidStatus
from ..dependencies import db_dependency, user_dependency


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_projects(
    db: db_dependency,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    status: str | None = None
):
    query = db.query(Project)

    if search:
        query = query.filter(
            or_(
                Project.title.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
        )

    if status:
        query = query.filter(Project.status == status)

    return query.offset(skip).limit(limit).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(user: user_dependency, db: db_dependency, project_request: CreateProjectRequest):

    project = Project(title=project_request.title, description=project_request.description,
                          budget=project_request.budget, owner_id=user.get('id'))
    db.add(project)
    db.commit()
    db.refresh(project)
    return {
        "message": "Project created successfully.",

    }


@router.get("/my", status_code=status.HTTP_200_OK,response_model=list[ProjectsResponse])
async def my_projects(user: user_dependency, db: db_dependency):

    projects = db.query(Project).filter(
        user.get('id') == Project.owner_id).all()
    return projects


@router.get("/{project_id}", status_code=status.HTTP_200_OK,response_model=ProjectsResponse)
async def find_by_id(user: user_dependency, db: db_dependency, project_id: int):

    project = db.query(Project).filter(project_id == Project.id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='project not found !'
        )
    return project


@router.put("/{project_id}", status_code=status.HTTP_200_OK)
async def change_project_info(user: user_dependency, db: db_dependency, project_id: int, new_info: CreateProjectRequest):

    project = db.query(Project).filter(Project.id == project_id).filter(
        user.get('id') == Project.owner_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='project not found !'
        )
    if project.status != ProjectStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail='project status is not open !'
        )
    for key, value in new_info.model_dump().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return {
        "message": "Project updated successfully."
    }



@router.patch("/{project_id}/bids/{bid_id}/accept", status_code=status.HTTP_201_CREATED)
async def accept_project(user: user_dependency, db: db_dependency, project_id: int, bid_id: int):

    project = db.query(Project).filter(
        Project.id == project_id, Project.owner_id == user.get('id')).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='project not found !'
        )
    if project.status != ProjectStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='project is already taken !'
        )
    bid = db.query(Bid).filter(Bid.id == bid_id,
                               Bid.project_id == project_id).first()

    if bid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='bid not found !'
        )

    bid.status = BidStatus.ACCEPTED
    otherbids = db.query(Bid).filter(
        Bid.project_id == project_id, Bid.id != bid_id).all()
    for i in otherbids:
        i.status = BidStatus.REJECTED
    project.winner_id = bid.freelancer_id
    project.status = ProjectStatus.IN_PROGRESS
    notification = Notification(
        user_id=bid.freelancer_id, title='bid accepted', message='Congratulations! Your bid has been accepted.', type=NotificationType.BID_ACCEPTED
    )
    db.add(notification)
    db.commit()
    return {
        "message": "Bid accepted successfully."
    }


@router.patch("/{project_id}/complete", status_code=status.HTTP_200_OK)
async def complete_project(user: user_dependency, db: db_dependency, project_id: int):

    project = db.query(Project).filter(
        Project.id == project_id, Project.owner_id == user.get('id')).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='project not found !'
        )
    if project.status == ProjectStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='project is already complete.'
        )

    if project.status != ProjectStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='project is not in progress to be completed.'
        )
    client_notification = Notification(
        user_id=project.owner_id, title='project completed', message='Project completed successfully.', type=NotificationType.PROJECT_COMPLETED
    )
    freelancer_notification = Notification(
        user_id=project.winner_id, title='project completed', message='Project completed successfully.', type=NotificationType.PROJECT_COMPLETED
    )
    db.add(client_notification)
    db.add(freelancer_notification)
    project.status = ProjectStatus.COMPLETED
    db.commit()
    return {
        "message": "Project completed successfully."
    }


@router.patch("/{project_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_project(user: user_dependency, db: db_dependency, project_id: int):

    project = db.query(Project).filter(
        Project.id == project_id, Project.owner_id == user.get('id')).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='project not found !'
        )
    if project.status == ProjectStatus.CANCELED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='project is already canceled.'
        )
    if project.status == ProjectStatus.COMPLETED or project.status == ProjectStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='project cannot be canceled.'
        )
    bids = db.query(Bid).filter(Bid.project_id == project_id).all()
    if bids:
        for i in bids:
            i.status = ProjectStatus.CANCELED

    project.status = ProjectStatus.CANCELED
    db.commit()
    return 'project canceled succesfully.'
