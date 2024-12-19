from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: List[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
