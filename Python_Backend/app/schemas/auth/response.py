from pydantic import BaseModel


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str


class MessageResponse(BaseModel):
    message: str