from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies.auth import (
    get_current_user,
)
from app.db.models.user import User

router = APIRouter(
    prefix="/test",
    tags=["Test"],
)


@router.get("/me")
async def me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "id": str(
            current_user.id
        ),
        "email":
            current_user.email,
    }