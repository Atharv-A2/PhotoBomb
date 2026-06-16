from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt

from app.core.config.settings import (
    get_settings,
)
from app.db.session.session import get_db
from app.db.models.user import User

from datetime import UTC
from datetime import datetime
from datetime import timedelta

from app.core.config.settings import (
    get_settings,
)
from app.core.security.auth import (
    hash_refresh_token,
)
from app.core.security.hashing import (
    hash_password,
    verify_password,
)
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.db.models.refresh_token import (
    RefreshToken,
)
from app.db.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

settings = get_settings()


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
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

    async for session in get_db():
        user = await session.get(
            User,
            user_id,
        )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user