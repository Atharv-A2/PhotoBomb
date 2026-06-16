from enum import StrEnum


class StorageProviderType(StrEnum):
    TELEGRAM = "TELEGRAM"
    S3 = "S3"
    MINIO = "MINIO"