from typing import Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.auth.models import User


class UserRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def create(
        self,
        data: dict[str, Any],
    ) -> User:
        user = User(**data)
        self.async_session.add(user)
        await self.async_session.commit()
        await self.async_session.refresh(user)
        return user

    async def get_single(
        self,
        **filters,
    ) -> User | None:
        query = select(User).filter_by(**filters)
        result = await self.async_session.execute(query)
        return result.scalar_one_or_none()

    async def get_multiple(
        self,
        order: str = "id",
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        query = select(User).order_by(order).offset(offset).limit(limit)

        result = await self.async_session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        data: dict[str, Any],
        **filters,
    ) -> User:
        stmt = update(User).filter_by(**filters).values(**data).returning(User)
        user = await self.async_session.execute(stmt)

        return user.scalar_one()

    async def delete(
        self,
        **filters,
    ) -> None:
        stmt = delete(User).filter_by(**filters)

        await self.async_session.execute(stmt)
        await self.async_session.commit()
