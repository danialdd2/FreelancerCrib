from fastapi import APIRouter, HTTPException, Path
from starlette import status
from ..models import User
from ..schemas import CreateUserRequest, UserResponse, ChangeInfo, userresponse
from ..dependencies import db_dependency, user_dependency
from ..auth import bcrypt_context

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        full_name=create_user_request.full_name,
        user_role=create_user_request.user_role,
        hashed_password=bcrypt_context.hash(create_user_request.password)
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return {"message": "User created successfully"}


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_info(user: user_dependency, db: db_dependency):

    the_user = db.query(User).filter(User.id == user.get('id')).first()
    return the_user


@router.put("/me")
async def change_info(user: user_dependency, db: db_dependency, new_info: ChangeInfo):

    the_user = db.query(User).filter(User.id == user.get('id')).first()
    for key, value in new_info.model_dump().items():
        setattr(the_user, key, value)
    db.commit()
    db.refresh(the_user)
    return {
        "message": "Profile updated successfully",
    }
    


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=userresponse)
async def get_user_info(user: user_dependency, db: db_dependency,user_id):

    the_user = db.query(User).filter(User.id == user_id).first()
    if the_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='authentication failed'
        )
    return the_user
