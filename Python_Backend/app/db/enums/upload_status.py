from enum import StrEnum


class UploadStatus(StrEnum):
    PENDING = "PENDING"
    INITIATING = "INITIATING"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    AVAILABLE = "AVAILABLE"
    FAILED = "FAILED"