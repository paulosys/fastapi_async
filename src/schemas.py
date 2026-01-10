from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
