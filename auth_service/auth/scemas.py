from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


class BaseChema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseChema):
    username: str
    email: EmailStr
    password: str


class UserGet(BaseChema):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool


class UserGetWithPassword(UserGet):
    hashed_password: str


class UserUpdate(BaseChema):
    username: str | None = None
    email: EmailStr | None = None


class Token(BaseChema):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
