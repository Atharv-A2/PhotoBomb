from pydantic import BaseModel


class InitiateUploadRequest(
    BaseModel
):
    filename: str
    size: int
    mime_type: str