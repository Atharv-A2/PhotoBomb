from pydantic import BaseModel


class ViewerResponse(
    BaseModel
):
    download_url: str