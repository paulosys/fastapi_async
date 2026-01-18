from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_async.database import get_session
from fastapi_async.models import Todo, User
from fastapi_async.schemas import (
    FilterTodoSchema,
    Message,
    TodoListSchema,
    TodoOutSchema,
    TodoSchema,
    TodoUpdateSchema,
)
from fastapi_async.security import get_current_user

router = APIRouter(tags=['todos'], prefix='/todos')

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
TodoFilter = Annotated[FilterTodoSchema, Query()]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=TodoOutSchema,
)
async def create_todo(
    todo: TodoSchema,
    session: Session,
    current_user: CurrentUser,
):
    todo = Todo(**todo.model_dump(), user_id=current_user.id)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return todo


@router.get(
    '/',
    response_model=TodoListSchema,
)
async def list_todos(
    session: Session,
    current_user: CurrentUser,
    todo_filter: TodoFilter,
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if todo_filter.title:
        query = query.where(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.where(Todo.description.contains(todo_filter.description))

    if todo_filter.state:
        query = query.where(Todo.state == todo_filter.state)

    todos = await session.scalars(
        query.limit(todo_filter.limit).offset(todo_filter.offset),
    )
    return {'todos': todos.all()}


@router.delete(
    '/{todo_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_todo(
    todo_id: int,
    session: Session,
    current_user: CurrentUser,
):
    todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    await session.delete(todo)
    await session.commit()

    return Message(message='Task deleted successfully!')


@router.patch('/{todo_id}', response_model=TodoOutSchema)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdateSchema,
    session: Session,
    current_user: CurrentUser,
):
    todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    for key, value in todo_data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)

    await session.commit()
    await session.refresh(todo)

    return todo
