from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.session.session import (
    get_db,
)
from app.schemas.auth.request import (
    RegisterRequest,
)
from app.schemas.auth.response import (
    UserResponse,
)
from app.services.auth.auth_service import (
    AuthService,
)
from app.schemas.auth.request import (
    LoginRequest,
)
from app.schemas.auth.response import (
    AuthResponse,
)
from app.schemas.auth.request import (
    RefreshRequest,
)
from app.schemas.auth.request import (
    LogoutRequest,
)
from app.schemas.auth.response import (
    MessageResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(
        get_db
    ),
):
    service = AuthService(
        session
    )

    try:
        return await service.register(
            request
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    

@router.post(
    "/login",
    response_model=AuthResponse,
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(
        get_db
    ),
):
    service = AuthService(
        session
    )

    try:
        return await service.login(
            request
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )
    
    
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login-swagger", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)

    request = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )

    try:
        return await service.login(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )
    

@router.post(
    "/refresh",
    response_model=AuthResponse,
)
async def refresh(
    request: RefreshRequest,
    session: AsyncSession = Depends(
        get_db
    ),
):
    service = AuthService(
        session
    )

    try:
        return await service.refresh(
            request
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )
    
    
@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(
    request: LogoutRequest,
    session: AsyncSession = Depends(
        get_db
    ),
):
    service = AuthService(
        session
    )

    try:
        await service.logout(
            request.refresh_token
        )

        return MessageResponse(
            message="Logged out"
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )