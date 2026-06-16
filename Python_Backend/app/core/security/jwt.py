from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

from jose import jwt

from app.core.config.settings import get_settings

settings = get_settings()


def create_access_token(
    user_id: str,
) -> str:
    expire = datetime.now(
        UTC
    ) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": user_id,
        "type": "access",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )


def create_refresh_token() -> str:
    return str(uuid4())