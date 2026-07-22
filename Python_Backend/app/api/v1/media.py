from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import File, Form
from fastapi import Request
from uuid import UUID
from datetime import datetime
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
from app.schemas.media.request import (
    BulkCreateUploadSessionRequest,
)
from app.schemas.media.response import (
    BulkUploadSessionResponse,
)
from app.schemas.media.status import (
    MediaStatusResponse,
)
from app.services.media.gallery_service import (
    GalleryService,
)
from app.services.media.viewer_service import (
    ViewerService,
)
from app.services.download.download_service import (
    DownloadService,
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
    

@router.post(
    "/upload-sessions/{upload_session_id}/file"
)
async def upload_file(
    upload_session_id: UUID,
    file: UploadFile = File(
        ...
    ),
    last_modified_at: datetime | None = 
        Form(None),
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
            service.upload_file(
                upload_session_id,
                current_user.id,
                file,
                last_modified_at,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    

@router.post(
    "/upload-sessions/bulk",
    response_model=
        BulkUploadSessionResponse,
)
async def create_bulk_upload_sessions(
    request:
        BulkCreateUploadSessionRequest,
    current_user: User =
        Depends(
            get_current_user
        ),
    session: AsyncSession =
        Depends(get_db),
):
    MAX_BULK_SESSION_SIZE = 1000
    
    service = UploadService(
        session
    )

    try:
        
        sessions = await (
            service.create_bulk_upload_sessions(
                current_user.id,
                request.files,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return (
        BulkUploadSessionResponse(
            sessions=sessions
        )
    )


@router.get("")
async def list_media(
    limit: int = 50,
    offset: int = 0,
    current_user: User =
        Depends(
            get_current_user
        ),
    session: AsyncSession =
        Depends(get_db),
):
    service = GalleryService(
        session
    )

    return await (
        service.list_media(
            current_user.id,
            limit,
            offset,
        )
    )


@router.get(
    "/{media_id}"
)
async def get_media(
    media_id: UUID,
    current_user: User =
        Depends(
            get_current_user
        ),
    session: AsyncSession =
        Depends(get_db),
):
    service = ViewerService(
        session
    )

    return await (
        service.get_detail(
            media_id
        )
    )


@router.get(
    "/{media_id}/viewer"
)
async def get_viewer(
    media_id: UUID,
    current_user: User =
        Depends(
            get_current_user
        ),
    session: AsyncSession =
        Depends(get_db),
):
    service = ViewerService(
        session
    )

    return await (
        service.get_viewer(
            media_id
        )
    )


@router.get(
    "/{media_id}/stream"
)
async def stream_media(
    media_id: UUID,
    request: Request,
    current_user: User =
        Depends(
            get_current_user
        ),
    session: AsyncSession =
        Depends(get_db),
):
    service = ViewerService(
        session
    )

    return await (
        service.stream_media(
            media_id,
            request
        )
    )


@router.get(
    "/thumbnails/{thumbnail_id}"
)
async def get_thumbnail(
    thumbnail_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    service = ViewerService(
        session
    )

    return await (
        service.get_thumbnail(
            thumbnail_id
        )
    )


@router.get(
    "/{media_id}/status",
    response_model=MediaStatusResponse,
)
async def get_status(
    media_id: UUID,
    session: AsyncSession = Depends(
        get_db
        ),
):
    service = ViewerService(session)

    return await (
        service.get_status(
            media_id
        )
    )


@router.get(
    "/{media_id}/download"
)
async def download_media(
    media_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = DownloadService(session)

    return await (
        service.download_media(
            media_id
        )
    )