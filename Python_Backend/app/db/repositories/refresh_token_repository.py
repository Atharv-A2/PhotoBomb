from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import UTC
from datetime import datetime

from app.db.models.refresh_token import (
    RefreshToken,
)


class RefreshTokenRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        token: RefreshToken,
    ):
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_hash(
        self,
        token_hash: str,
    ):
        stmt = select(
            RefreshToken
        ).where(
            RefreshToken.token_hash
            == token_hash
        )

        result = await self.session.execute(
            stmt
        )

        return (
            result.scalar_one_or_none()
        )
    

    async def revoke(
        self,
        token: RefreshToken,
    ):
        token.revoked_at = (
            datetime.now(UTC)
        )

        await self.session.flush()