from datetime import UTC
from datetime import datetime
from datetime import timedelta

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.core.security.hashing import (
    hash_password,
)
from app.db.models.user import User
from app.db.repositories.user_repository import (
    UserRepository,
)
from app.schemas.auth.request import (
    RegisterRequest,
)
from app.schemas.auth.response import (
    UserResponse,
)
from app.core.config.settings import (
    get_settings,
)
from app.core.security.auth import (
    hash_refresh_token,
)
from app.core.security.hashing import (
    verify_password,
)
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.db.models.refresh_token import (
    RefreshToken,
)
from app.db.repositories.refresh_token_repository import (
    RefreshTokenRepository,
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

settings = get_settings()


class AuthService:

    def __init__(
        self,
        session,
    ):
        self.session = session
        self.users = UserRepository(
            session
        )
        self.refresh_tokens = (
            RefreshTokenRepository(
                session
            )
        )

    async def register(
        self,
        request: RegisterRequest,
    ) -> UserResponse:

        total_users = (
            await self.users.count_users()
        )

        if total_users > 0:
            raise ValueError(
                "Registration disabled"
            )

        existing = (
            await self.users.get_by_email(
                request.email
            )
        )

        if existing:
            raise ValueError(
                "Email already exists"
            )

        user = User(
            email=request.email,
            password_hash=hash_password(
                request.password
            ),
        )

        await self.users.create(user)

        await self.session.commit()
        await self.session.refresh(user)

        return UserResponse(
            id=user.id,
            email=user.email,
        )
    

    async def login(
        self,
        request: LoginRequest,
    ) -> AuthResponse:

        user = (
            await self.users.get_by_email(
                request.email
            )
        )

        if (
            user is None
            or not verify_password(
                request.password,
                user.password_hash,
            )
        ):
            raise ValueError(
                "Invalid credentials"
            )

        access_token = (
            create_access_token(
                str(user.id)
            )
        )

        refresh_token = (
            create_refresh_token()
        )

        refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(
                refresh_token
            ),
            device_name=(
                request.device_name
            ),
            expires_at=(
                datetime.now(UTC)
                + timedelta(
                    days=settings.refresh_token_expire_days
                )
            ),
        )

        await (
            self.refresh_tokens.create(
                refresh
            )
        )

        await self.session.commit()

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=(
                settings.access_token_expire_minutes
                * 60
            ),
        )
    

    async def refresh(
        self,
        request: RefreshRequest,
    ) -> AuthResponse:

        token_hash = (
            hash_refresh_token(
                request.refresh_token
            )
        )

        token = (
            await self.refresh_tokens
            .get_by_hash(
                token_hash
            )
        )

        if token is None:
            raise ValueError(
                "Invalid refresh token"
            )

        if token.revoked_at:
            raise ValueError(
                "Refresh token revoked"
            )

        if (
            token.expires_at
            <= datetime.now(UTC)
        ):
            raise ValueError(
                "Refresh token expired"
            )

        user = await self.session.get(
            User,
            token.user_id,
        )

        if user is None:
            raise ValueError(
                "User not found"
            )

        await self.refresh_tokens.revoke(
            token
        )

        new_access_token = (
            create_access_token(
                str(user.id)
            )
        )

        new_refresh_token = (
            create_refresh_token()
        )

        new_refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(
                new_refresh_token
            ),
            device_name=token.device_name,
            expires_at=(
                datetime.now(UTC)
                + timedelta(
                    days=settings
                    .refresh_token_expire_days
                )
            ),
        )

        await (
            self.refresh_tokens.create(
                new_refresh
            )
        )

        await self.session.commit()

        return AuthResponse(
            access_token=
                new_access_token,
            refresh_token=
                new_refresh_token,
            expires_in=(
                settings
                .access_token_expire_minutes
                * 60
            ),
        )
    

    async def logout(
        self,
        refresh_token: str,
    ):
        token_hash = (
            hash_refresh_token(
                refresh_token
            )
        )

        token = (
            await self.refresh_tokens
            .get_by_hash(
                token_hash
            )
        )

        if token is None:
            raise ValueError(
                "Invalid refresh token"
            )

        if token.revoked_at:
            return

        await self.refresh_tokens.revoke(
            token
        )

        await self.session.commit()