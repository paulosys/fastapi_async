from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from schemas import (
    ErrorSchema,
    Message,
    UserDBSchema,
    UserListSchema,
    UserOutSchema,
    UserSchema,
)

app = FastAPI()
database: list[UserDBSchema] = []  # This will act as our in-memory database


@app.get('/', response_model=Message)
def read_root():
    return Message(message='Hello, World!')


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserOutSchema,
)
def create_user(user: UserSchema):
    user_id = len(database) + 1
    user_db = UserDBSchema(id=user_id, **user.model_dump())
    database.append(user_db)
    return user_db


@app.get(
    '/users/',
    status_code=HTTPStatus.OK,
    response_model=UserListSchema,
)
def list_users():
    return {'users': database}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserOutSchema,
    responses={HTTPStatus.NOT_FOUND: {'model': ErrorSchema}},
)
def update_user(user_id: int, user: UserSchema):
    for index, existing_user in enumerate(database):
        if existing_user.id == user_id:
            updated_user = UserDBSchema(id=user_id, **user.model_dump())
            database[index] = updated_user
            return updated_user

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='User not found!',
    )


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={HTTPStatus.NOT_FOUND: {'model': ErrorSchema}},
)
def delete_user(user_id: int):
    for index, existing_user in enumerate(database):
        if existing_user.id == user_id:
            del database[index]
            return

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='User not found!',
    )
