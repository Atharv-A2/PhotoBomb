from pydantic import BaseModel


class MediaStatusResponse(BaseModel):

    media_id: str

    status: str