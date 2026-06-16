from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def add(self, instance):
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(
        self,
        model,
        obj_id,
    ):
        stmt = select(model).where(
            model.id == obj_id
        )

        result = await self.session.execute(
            stmt
        )

        return result.scalar_one_or_none()