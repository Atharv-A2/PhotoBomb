from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository():

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        stmt = select(User).where(
            User.email == email
        )

        result = await self.session.execute(
            stmt
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        user: User,
    ) -> User:
        self.session.add(user)
        await self.session.flush()
        return user
    
    
    async def count_users(
        self,
    ) -> int:
        result = await self.session.execute(
            select(User)
        )

        return len(
            result.scalars().all()
        )