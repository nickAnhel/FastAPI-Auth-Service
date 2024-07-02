from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError, CompileError, DBAPIError

from auth_service.auth.scemas import UserCreate, UserGet
from auth_service.auth.service import UserService
from auth_service.auth.dependencies import get_user_service
from auth_service.auth.exceptions import UserNotFound


auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@auth_router.post("/register")
async def register_new_user(
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


@auth_router.post("/login")
async def get_jwt_token():
    pass


@auth_router.post("/refresh")
async def refresh_access_token():
    pass


@auth_router.post("/logout")
async def logout_user():
    pass


@user_router.get("/")
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
            detail="Limit and offset can't be less than 0",
        ) from exc


@user_router.get("/{username}")
async def get_user_by_username(
    username: str,
    user_service: UserService = Depends(get_user_service),
) -> UserGet:
    try:
        return await user_service.get_user(username=username)  # type: ignore
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc



@user_router.delete("/{username}")
async def delete_user_by_username(
    username: str,
    user_service: UserService = Depends(get_user_service),
):
    # try:
    await user_service.delete_user(username=username)
    # except UserNotFound as exc:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=str(exc),
    #     ) from exc
