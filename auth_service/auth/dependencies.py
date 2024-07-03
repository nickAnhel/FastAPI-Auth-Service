from typing import Any, Callable, Coroutine
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

from auth_service.database import get_async_session
from auth_service.auth.service import UserService
from auth_service.auth.repository import UserRepository
from auth_service.auth.scemas import UserGet, UserGetWithPassword
from auth_service.auth.utils import decode_jwt, validate_password, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from auth_service.auth.exceptions import UserNotFound


http_bearer = HTTPBearer()


async def get_user_service(
    async_session=Depends(get_async_session),
) -> UserService:
    repository = UserRepository(async_session)
    return UserService(repository)


async def authenticate_user(
    username: str = Form(...),
    password: str = Form(...),
    user_service: UserService = Depends(get_user_service),
) -> UserGetWithPassword:
    try:
        user: UserGetWithPassword = await user_service.get_user(  # type: ignore
            include_password=True,
            username=username,
        )
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
        ) from exc

    if not validate_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def _get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict[str, Any]:
    token = credentials.credentials
    try:
        return decode_jwt(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


def get_current_user_by_token_type(
    token_type: str
) -> Callable[..., Coroutine[Any, Any, UserGet]]:
    async def get_current_user_by_token_type_wrapper(
        user_service: UserService = Depends(get_user_service),
        token_payload: dict[str, Any] = Depends(_get_token_payload),
    ) -> UserGet:
        given_token_type = token_payload.get("type")
        if given_token_type != token_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid token type {given_token_type!r}, expected {token_type!r}",
            )

        try:
            user = await user_service.get_user(id=token_payload.get("sub"))
        except UserNotFound as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization token",
            ) from exc

        return user

    return get_current_user_by_token_type_wrapper


get_current_user = get_current_user_by_token_type(ACCESS_TOKEN_TYPE)
get_current_user_for_refresh = get_current_user_by_token_type(REFRESH_TOKEN_TYPE)


async def get_current_active_user(
    user: UserGet = Depends(get_current_user),
) -> UserGet:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user
