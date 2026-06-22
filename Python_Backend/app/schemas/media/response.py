from pydantic import BaseModel


class InitiateUploadResponse(
    BaseModel
):
    upload_id: str
    status: str


class UploadResponse(
    BaseModel
):
    media_id: str
    status: str