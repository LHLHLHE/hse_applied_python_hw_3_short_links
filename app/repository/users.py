from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas import UserCreateSchema


class UsersRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_user(self, user: UserCreateSchema) -> User:
        query = insert(User).values(**user.model_dump()).returning(User.id)
        async with self.db_session as session:
            user_id: int = (await session.execute(query)).scalar()
            await session.commit()
            await session.flush()
        return await self.get_user(user_id)

    async def get_user(self, user_id: int) -> User | None:
        async with self.db_session as session:
            return (await session.execute(
                select(User).where(User.id == user_id)
            )).scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        async with self.db_session as session:
            return (await session.execute(
                select(User).where(User.username == username)
            )).scalar_one_or_none()
