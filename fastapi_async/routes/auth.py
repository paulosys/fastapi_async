from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from fastapi_async.database import get_session
from fastapi_async.models import User
from fastapi_async.schemas import TokenSchema
from fastapi_async.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=TokenSchema)
async def login_for_access_token(
    form_data: OAuth2Form,
    session: Session,
):
    user = await session.scalar(
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

    return TokenSchema(access_token=token, token_type='Bearer')


@router.post('/refresh-token', response_model=TokenSchema)
async def refresh_access_token(
    current_user: Annotated[User, Depends(get_current_user)],
):
    token = create_access_token(data={'sub': current_user.username})

    return TokenSchema(access_token=token, token_type='Bearer')
