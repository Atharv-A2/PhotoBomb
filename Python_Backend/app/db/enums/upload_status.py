from enum import StrEnum


class UploadStatus(StrEnum):
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    AVAILABLE = "AVAILABLE"
    FAILED = "FAILED"