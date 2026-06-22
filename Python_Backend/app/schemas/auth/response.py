from pydantic import BaseModel
from uuid import UUID


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class UserResponse(BaseModel):
    id: UUID
    email: str


class MessageResponse(BaseModel):
    message: str