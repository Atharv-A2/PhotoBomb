from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.core.dependencies.auth import (
    get_current_user,
)
from app.db.models.user import User
from app.db.session.session import (
    get_db,
)
from app.schemas.media.request import (
    CreateUploadSessionRequest,
)
from app.schemas.media.response import (
    UploadSessionResponse,
)
from app.services.media.upload_service import (
    UploadService,
)

router = APIRouter(
    prefix="/media",
    tags=["Media"],
)


@router.post(
    "/upload-sessions",
    response_model=
        UploadSessionResponse,
)
async def create_upload_session(
    request:
        CreateUploadSessionRequest,
    current_user: User =
        Depends(
            get_current_user
        ),
    session: AsyncSession =
        Depends(get_db),
):
    service = UploadService(
        session
    )

    try:
        return await (
            service
            .create_upload_session(
                current_user.id,
                request,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )