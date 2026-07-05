from fastapi import APIRouter,  HTTPException
from starlette import status
from ..schemas import notificationresponse
from ..models import Notification
from ..dependencies import db_dependency, user_dependency


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[notificationresponse])
async def all_notofications(user: user_dependency, db: db_dependency):
    messages = db.query(Notification).filter(
        Notification.user_id == user.get('id')).all()
    if not messages:
        raise HTTPException(
            status_code=404, detail='no new notifications'
        )
    return messages


@router.get("/unread", status_code=status.HTTP_200_OK, response_model=list[notificationresponse])
async def unread_notifications(user: user_dependency, db: db_dependency):
    messages = db.query(Notification).filter(
        Notification.user_id == user.get('id'), Notification.is_read != True).all()
    if not messages:
        raise HTTPException(
            status_code=404, detail='no new notifications'
        )
    return messages


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def read_notification_by_id(user: user_dependency, db: db_dependency, notification_id:int):
    message = db.query(Notification).filter(Notification.user_id == user.get(
        'id'), Notification.id == notification_id).first()
    if message is None:
        raise HTTPException(
            status_code=404, detail='notification not found'
        )
    message.is_read = True
    db.commit()
    db.refresh(message)
    return message


@router.patch("/read-all", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    messages = db.query(Notification).filter(
        Notification.user_id == user.get('id')).all()

    for i in messages:
        i.is_read = True

    db.commit()
    return 'messages read succesfully'


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
async def delete_notification(user: user_dependency, db: db_dependency, notification_id:int):
    message = db.query(Notification).filter(Notification.user_id == user.get(
        'id'), Notification.id == notification_id).first()
    if message is None:
        raise HTTPException(
            status_code=404, detail='notification not found'
        )
    db.delete(message)
    db.commit()
    return 'message deleted succesfully'


@router.get("/unread-count", status_code=status.HTTP_200_OK)
async def unread_count(user: user_dependency, db: db_dependency):
    unreads = db.query(Notification).filter(Notification.user_id == user.get(
        'id'), Notification.is_read != True).count()
    unreads = unreads or 0
    return unreads
