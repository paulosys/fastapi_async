from pydantic import BaseModel, EmailStr


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


class UserDBSchema(UserSchema):
    id: int


class UserListSchema(BaseModel):
    users: list[UserOutSchema]
