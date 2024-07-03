from auth_service.auth.scemas import UserCreate, UserGet, UserGetWithPassword, UserUpdate
from auth_service.auth.repository import UserRepository
from auth_service.auth.exceptions import UserNotFound
from auth_service.auth.utils import get_password_hash


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository: UserRepository = repository

    async def create_user(self, data: UserCreate) -> UserGet:
        """Create new user."""
        user_data = data.model_dump()
        user_data["hashed_password"] = get_password_hash(user_data["password"])
        del user_data["password"]

        user = await self.repository.create(data=user_data)
        return UserGet.model_validate(user)

    async def get_user(
        self,
        include_password: bool = False,
        **filters,
    ) -> UserGet | UserGetWithPassword:
        """Get user by filters (username, email or id)."""
        user = await self.repository.get_single(**filters)

        if not user:
            raise UserNotFound(f"User with filters {filters} not found")

        return UserGetWithPassword.model_validate(user) if include_password else UserGet.model_validate(user)

    async def get_users(
        self,
        order: str = "id",
        offset: int = 0,
        limit: int = 100,
    ) -> list[UserGet]:
        """Get users with pagination."""
        users = await self.repository.get_multiple(
            order=order,
            offset=offset,
            limit=limit,
        )
        return [UserGet.model_validate(user) for user in users]

    async def update_user(
        self,
        data: UserUpdate,
        **filters,
    ) -> UserGet:
        """Update user by filters (username, email or id)."""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        user = await self.repository.update(data=update_data, **filters)
        return UserGet.model_validate(user)

    async def delete_user(self, **filters) -> None:
        """Delete user by filters (username, email or id)."""
        await self.repository.delete(**filters)
