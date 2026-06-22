from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import (
    get_settings,
)
from app.db.models.user import User
from app.db.session.session import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login-swagger"
)

settings = get_settings()


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    session: AsyncSession = Depends(
        get_db
    ),
):
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )

        user_id = payload["sub"]

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = await session.get(
        User,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User inactive",
        )

    return user