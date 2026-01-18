from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_async.models import TodoState


class Message(BaseModel):
    message: str


class ErrorSchema(BaseModel):
    detail: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOutSchema(BaseModel):
    username: str
    email: EmailStr
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserListSchema(BaseModel):
    users: list[UserOutSchema]


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class FilterPageSchema(BaseModel):
    limit: int = Field(10, ge=1)
    offset: int = Field(0, ge=0)


class TodoSchema(BaseModel):
    title: str
    description: str | None = None
    state: TodoState = Field(default=TodoState.TODO)


class TodoOutSchema(TodoSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class FilterTodoSchema(FilterPageSchema):
    title: str | None = Field(default=None, min_length=3)
    description: str | None = None
    state: TodoState | None = None


class TodoListSchema(BaseModel):
    todos: list[TodoOutSchema]


class TodoUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
