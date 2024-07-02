from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


class BaseUserChema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseUserChema):
    username: str
    email: EmailStr
    password: str


class UserGet(BaseUserChema):
    id: UUID
    username: str
    email: EmailStr
