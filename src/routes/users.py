from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session as SessionType
from typing_extensions import Annotated

from database import get_session
from models import User
from schemas import (
    ErrorSchema,
    FilterPageSchema,
    Message,
    UserListSchema,
    UserOutSchema,
    UserSchema,
)
from security import get_current_user, get_hashed_password

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[SessionType, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserOutSchema,
)
def create_user(user: UserSchema, session: Session):
    db_user = session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User with this email or username already exists!',
        )

    db_user = User(**user.model_dump())
    db_user.password = get_hashed_password(user.password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=UserListSchema,
)
def list_users(
    session: Session,
    current_user: CurrentUser,
    filter_page: Annotated[FilterPageSchema, Query()],
):
    users = session.scalars(
        (select(User).limit(filter_page.limit).offset(filter_page.offset))
    )
    return {'users': users}


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserOutSchema,
    responses={HTTPStatus.NOT_FOUND: {'model': ErrorSchema}},
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to update this user!',
        )

    existing_user = session.scalar(
        select(User).where(
            ((User.email == user.email) | (User.username == user.username))
            & (User.id != user_id)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User with this email or username already exists!',
        )

    for key, value in user.model_dump().items():
        setattr(current_user, key, value)

    current_user.password = get_hashed_password(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.NOT_FOUND: {'model': ErrorSchema}},
)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to delete this user!',
        )

    session.delete(current_user)
    session.commit()

    return Message(message='User deleted successfully!')
