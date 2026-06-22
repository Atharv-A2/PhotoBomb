SUPPORTED_IMAGES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
}

SUPPORTED_VIDEOS = {
    "video/mp4",
    "video/quicktime",
    "video/x-matroska",
    "video/3gpp",
}


def validate_mime_type(
    mime_type: str,
):
    supported = (
        SUPPORTED_IMAGES
        | SUPPORTED_VIDEOS
    )

    if mime_type not in supported:
        raise ValueError(
            "Unsupported media type"
        )