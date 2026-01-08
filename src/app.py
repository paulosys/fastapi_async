from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import User
from schemas import (
    ErrorSchema,
    Message,
    TokenSchema,
    UserListSchema,
    UserOutSchema,
    UserSchema,
)
from security import (
    create_access_token,
    get_current_user,
    get_hashed_password,
    verify_password,
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
    db_user.password = get_hashed_password(user.password)

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
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.NOT_FOUND: {'model': ErrorSchema}},
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to delete this user!',
        )

    session.delete(current_user)
    session.commit()

    return Message(message='User deleted successfully!')


@app.post('/token', response_model=TokenSchema)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(
        select(User).where(
            (User.username == form_data.username)
            | (User.email == form_data.username)
        )
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    token = create_access_token(data={'sub': user.username})

    return TokenSchema(access_token=token, token_type='bearer')
