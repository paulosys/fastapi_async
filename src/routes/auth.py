from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session as SessionType
from typing_extensions import Annotated

from database import get_session
from models import User
from schemas import TokenSchema
from security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[SessionType, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=TokenSchema)
def login_for_access_token(
    form_data: OAuth2Form,
    session: Session,
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
