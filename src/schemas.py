from pydantic import BaseModel, ConfigDict, EmailStr


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
