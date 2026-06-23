from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.session.session import (
    get_db,
)

from app.db.repositories.media_thumbnail_repository import (
    MediaThumbnailRepository,
)

router = APIRouter(
    prefix="/thumbnails",
    tags=["Thumbnails"],
)


@router.get(
    "/{thumbnail_id}"
)
async def get_thumbnail(
    thumbnail_id,
    session: AsyncSession =
        Depends(get_db),
):
    repo = (
        MediaThumbnailRepository(
            session
        )
    )

    thumbnail = (
        await repo.get(
            thumbnail_id
        )
    )

    if thumbnail is None:
        raise HTTPException(
            status_code=404,
            detail="Thumbnail not found",
        )

    return FileResponse(
        thumbnail.path,
        media_type="image/webp",
    )


