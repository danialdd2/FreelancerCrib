from fastapi import APIRouter, Path
from starlette import status
from ..models import Project, Rating, Bid
from sqlalchemy import func
from ..dependencies import db_dependency, user_dependency
from ..schemas import FreelancerDashboardResponse,ClientDashboardResponse
from ..enums import ProjectStatus,BidStatus


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=ClientDashboardResponse|FreelancerDashboardResponse)
async def dashboard(db: db_dependency, user: user_dependency):

    print(user.get('role'))
    print(user.get('user_role'))

    if user.get("user_role") == "client":
        projects_created = db.query(Project).filter(
            Project.owner_id == user.get("id")).count()
        client_completed_projects = db.query(Project).filter(
            Project.owner_id == user.get("id"), Project.status == ProjectStatus.COMPLETED).count()
        client_active_projects = db.query(Project).filter(
            Project.owner_id == user.get("id"), Project.status == ProjectStatus.IN_PROGRESS).count()
        client_total_bids = db.query(Bid).join(Project).filter(
            Project.owner_id == user.get("id")).count()
        rating = (db.query(func.avg(Rating.score)).filter(
            Rating.to_user_id == user.get("id")).scalar())
        rating = rating or 0
        client_open_projects = db.query(Project).filter(
            Project.owner_id == user.get('id'), Project.status == ProjectStatus.OPEN).count()
        return {"projects_created": projects_created, "projects_completed": client_completed_projects,
                "client_open_projects": client_open_projects, "active_projects": client_active_projects,
                "total_bids": client_total_bids, "rating": rating
                }
    else:
        freelancer_active_projects = db.query(Project).filter(
            Project.winner_id == user.get("id"), Project.status == ProjectStatus.IN_PROGRESS).count()
        freelancer_completed_projects = db.query(Project).filter(
            Project.winner_id == user.get("id"), Project.status == ProjectStatus.COMPLETED).count()
        total_bids_sent = db.query(Bid).filter(
            Bid.freelancer_id == user.get("id")).count()

        rating = (db.query(func.avg(Rating.score)).filter(
            Rating.to_user_id == user.get("id")).scalar())
        rating = rating or 0
        projects_won = db.query(Project).filter(
            Project.winner_id == user.get("id")).count()
        pending_bids = db.query(Bid).filter(
            Bid.freelancer_id == user.get('id'), Bid.status == BidStatus.PENDING).count()
        return {"bids_sent": total_bids_sent, "pending_bids": pending_bids,
                "projects_won": projects_won, "projects_completed": freelancer_completed_projects,
                "active_projects": freelancer_active_projects, "rating": rating}
