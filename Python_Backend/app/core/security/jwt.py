from datetime import UTC
from datetime import datetime
from datetime import timedelta
import secrets

from jose import jwt

from app.core.config.settings import get_settings

settings = get_settings()


def create_access_token(
    user_id: str,
) -> str:
    expire = (
        datetime.now(UTC)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)