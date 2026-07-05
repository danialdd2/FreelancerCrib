from fastapi import APIRouter, HTTPException, Path
from starlette import status
from ..models import Project, Bid, Notification
from ..schemas import CreateBidRequest, bidsresponse
from ..enums import NotificationType,BidStatus,ProjectStatus
from ..dependencies import db_dependency, user_dependency


router = APIRouter(
    tags=["Bids"]
)


@router.post("/projects/{project_id}/bids", status_code=status.HTTP_201_CREATED)
async def new_bid(user: user_dependency, db: db_dependency, project_id: int, bidrequest: CreateBidRequest):

    theproject = db.query(Project).filter(Project.id == project_id).first()
    if theproject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    if theproject.owner_id == user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=' you cant send bid on your project'
        )
    if theproject.status == ProjectStatus.CANCELED or theproject.status == ProjectStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='project is canceled or completed'
        )
    existing_bid = db.query(Bid).filter(
        Bid.project_id == project_id, Bid.freelancer_id == user.get("id")).first()

    if existing_bid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='you have already sent bid on this project'
        )

    thebid = Bid(price=bidrequest.price, message=bidrequest.message,
                 project_id=theproject.id, freelancer_id=user.get('id'))
    notification = Notification(
        user_id=theproject.owner_id, title='new bid', message='you have a new bid request', type=NotificationType.NEW_BID
    )

    db.add(thebid)
    db.add(notification)
    db.commit()
    db.refresh(thebid)
    return {
        "message": "Bid submitted successfully",

    }


@router.get("/projects/{project_id}/bids", status_code=status.HTTP_200_OK)
async def get_project_bids(user: user_dependency, db: db_dependency, project_id: int):

    theproject = db.query(Project).filter(Project.id == project_id).filter(
        Project.owner_id == user.get('id')).first()
    if theproject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='project not found'
        )

    bids = db.query(Bid).filter(Bid.project_id == project_id).all()
    if not bids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='no bids on this project yet ):'
        )
    return bids


@router.get("/users/me/bids", status_code=status.HTTP_200_OK, response_model=list[bidsresponse])
async def my_bids(user: user_dependency, db: db_dependency):

    bids = db.query(Bid).filter(Bid.freelancer_id == user.get('id')).all()
    if not bids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='you have no bids'
        )
    return bids


@router.put("/bids/{bid_id}", status_code=status.HTTP_200_OK)
async def update_bid(user: user_dependency, db: db_dependency, bid_id: int, new_info: CreateBidRequest):

    bid = db.query(Bid).filter(Bid.id == bid_id,
                               Bid.freelancer_id == user.get("id")).first()
    if bid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='bid not found'
        )
    for key, value in new_info.model_dump().items():
        setattr(bid, key, value)

    db.commit()
    db.refresh(bid)

    return {
        "message": "Bid updated successfully",

    }


@router.delete("/bids/{bid_id}", status_code=status.HTTP_200_OK)
async def delete_bid(user: user_dependency, db: db_dependency, bid_id: int):

    bid = db.query(Bid).filter(Bid.id == bid_id,
                               Bid.freelancer_id == user.get("id")).first()
    if bid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='bid not found')
    db.delete(bid)
    db.commit()
    return {
        "message": "Bid deleted successfully"
    }
