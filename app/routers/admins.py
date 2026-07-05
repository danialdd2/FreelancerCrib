from fastapi import APIRouter, HTTPException, Path
from starlette import status
from ..models import User
from ..dependencies import db_dependency, user_dependency
from ..enums import UserType

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency, user: user_dependency):
    if user.get('role') != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required'
        )
    return db.query(User).all()


@router.patch("/admin/users/{user_id}/role")
async def add_admin(user: user_dependency, db: db_dependency, user_id: int):
    # if user.get('role') != UserType.ADMIN:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required'
    #     )
    theuser = db.query(User).filter(User.id == user_id).first()
    if theuser.role == UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='user already has admin access'
        )
    theuser.role = UserType.ADMIN
    db.commit()
    return {
        "message": "User promoted to admin successfully"
    }


@router.get("/admins", status_code=status.HTTP_200_OK)
async def get_all_admins(user: user_dependency, db: db_dependency):
    if user.get('role') != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required'
        )
    admins = db.query(User).filter(User.role == UserType.ADMIN).all()
    return admins
