from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.session.session import get_db

router = APIRouter(
    prefix="/test-db",
    tags=["Test DB"],
)


@router.get("/")
async def test_db(
    session: AsyncSession = Depends(
        get_db
    )
):
    result = await session.execute(
        text("SELECT 1")
    )

    return {
        "result":
            result.scalar()
    }