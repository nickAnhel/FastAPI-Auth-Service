from sqlalchemy.exc import IntegrityError, CompileError, DBAPIError
from fastapi import APIRouter, HTTPException, Depends, status

from auth_service.auth.service import UserService
from auth_service.auth.exceptions import UserNotFound
from auth_service.auth.utils import create_access_token, create_refresh_token
from auth_service.auth.scemas import (
    UserCreate,
    UserGet,
    UserGetWithPassword,
    UserUpdate,
    Token,
)
from auth_service.auth.dependencies import (
    get_current_active_user,
    get_user_service,
    authenticate_user,
    get_current_user,
    get_current_user_for_refresh,
)


auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# JWT auth endpoints
@auth_router.post("/login")
async def get_jwt_token(
    user: UserGetWithPassword = Depends(authenticate_user),
) -> Token:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@auth_router.post("/refresh", response_model_exclude_none=True)
async def refresh_access_token(user: UserGet = Depends(get_current_user_for_refresh)) -> Token:
    access_token = create_access_token(user)

    return Token(
        access_token=access_token,
    )


# Users endpoints
@users_router.post("/")
async def create_user(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserGet:
    try:
        return await user_service.create_user(data=data)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        ) from exc


@users_router.get("/me")
def get_current_user_info(
    user: UserGet = Depends(get_current_user),
) -> UserGet:
    return user


@users_router.get("/")
async def get_users(
    order: str = "id",
    offset: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
) -> list[UserGet]:
    try:
        return await user_service.get_users(order=order, offset=offset, limit=limit)
    except CompileError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid value of order",
        ) from exc
    except DBAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit and offset must be positive integers or 0",
        ) from exc


@users_router.get("/{username}")
async def get_user_by_username(
    username: str,
    user_service: UserService = Depends(get_user_service),
) -> UserGet:
    try:
        return await user_service.get_user(username=username)  # type: ignore
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc


@users_router.put("/")
async def update_user(
    data: UserUpdate,
    user: UserGet = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserGet:
    try:
        return await user_service.update_user(data=data, id=user.id)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        ) from exc


@users_router.delete("/")
async def delete_user(
    user: UserGet = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    await user_service.delete_user(id=user.id)
