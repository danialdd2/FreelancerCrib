from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from .schemas import Token
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from .models import User
from passlib.context import CryptContext
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from jose import jwt, JWTError
from .config import settings
from .database import get_db

db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        user_role: str = payload.get('user_role')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
        return {'username': username, 'id': user_id, 'role': role, 'user_role': user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')


def create_access_token(username: str, user_id: int, role: str, user_role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc)+expires_delta
    encode = {'sub': username, 'id': user_id,
              'exp': expires, 'role': role, 'user_role': user_role}
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    token = create_access_token(
        user.username, user.id, user.role, user.user_role, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    return {'access_token': token, 'token_type': 'bearer'}
