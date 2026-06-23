from pydantic import BaseModel
from pydantic import Field
from typing import List


class CreateUploadSessionRequest(
    BaseModel
):
    filename: str = Field(
        min_length=1,
        max_length=512,
    )

    file_size: int = Field(
        gt=0
    )

    mime_type: str


class BulkCreateUploadSessionRequest(
    BaseModel,
):
    files: List[
        CreateUploadSessionRequest
    ]