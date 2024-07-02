from fastapi import Depends

from auth_service.database import get_async_session
from auth_service.auth.service import UserService
from auth_service.auth.repository import UserRepository


async def get_user_service(
    async_session=Depends(get_async_session),
) -> UserService:
    repository = UserRepository(async_session)
    return UserService(repository)
