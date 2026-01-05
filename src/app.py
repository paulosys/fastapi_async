from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import User
from schemas import (
    ErrorSchema,
    Message,
    UserListSchema,
    UserOutSchema,
    UserSchema,
)

app = FastAPI()


@app.get('/', response_model=Message)
def read_root():
    return Message(message='Hello, World!')


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserOutSchema,
)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
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

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get(
    '/users/',
    status_code=HTTPStatus.OK,
    response_model=UserListSchema,
)
def list_users(
    limit: int = 10, offset: int = 0, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserOutSchema,
    responses={HTTPStatus.NOT_FOUND: {'model': ErrorSchema}},
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found!',
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
        setattr(db_user, key, value)

    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.NOT_FOUND: {'model': ErrorSchema}},
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found!',
        )

    session.delete(db_user)
    session.commit()

    return Message(message='User deleted successfully!')
