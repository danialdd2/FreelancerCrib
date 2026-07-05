from fastapi import APIRouter, HTTPException, Path
from starlette import status
from ..schemas import CreateRatingRequest
from ..models import Project, Rating, Notification
from ..enums import NotificationType,ProjectStatus
from ..dependencies import db_dependency, user_dependency


router = APIRouter(
    tags=["Ratings"]
)


@router.post("/projects/{project_id}/ratings", status_code=status.HTTP_201_CREATED)
async def create_rating(user: user_dependency, db: db_dependency, project_id: int, rate: CreateRatingRequest):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='project not found !'
        )
    if user.get("id") not in (project.owner_id, project.winner_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='project not found !'
        )
    if project.status != ProjectStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='project has to be completed'
        )
    to_user = (project.winner_id if user.get("id") ==
               project.owner_id else project.owner_id)

    rating = Rating(
        project_id=project.id,
        score=rate.score,
        comment=rate.comment,
        from_user_id=user.get("id"),
        to_user_id=to_user,)

    existing = (db.query(Rating).filter(
        Rating.project_id == project.id,
        Rating.from_user_id == user.get("id")).first())

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You have already rated this project."
        )
    notification = Notification(
        user_id=to_user, title='new rating', message='You received a new rating.', type=NotificationType.RATING_RECEIVED
    )
    db.add(rating)
    db.add(notification)
    db.commit()
    db.refresh(rating)
    return {
        "message": "Rating submitted successfully"
    }
