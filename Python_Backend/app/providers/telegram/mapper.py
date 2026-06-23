from app.services.storage.models import (
    StorageUploadResult,
)


class TelegramMapper:

    @staticmethod
    def to_upload_result(
        result: dict,
    ):
        if "document" in result:
            media = result["document"]
            telegram_type = "document"

        elif "video" in result:
            media = result["video"]
            telegram_type = "video"

        else:
            raise RuntimeError(
                f"Unsupported Telegram payload: {result}"
            )

        chat = result["chat"]

        metadata = {
            "telegram_media_type":
                telegram_type,

            "chat_id":
                chat["id"],

            "message_id":
                result["message_id"],

            "file_id":
                media["file_id"],

            "file_unique_id":
                media["file_unique_id"],

            "file_name":
                media.get("file_name"),

            "mime_type":
                media.get("mime_type"),

            "file_size":
                media.get("file_size"),

            "width":
                media.get("width"),

            "height":
                media.get("height"),

            "duration":
                media.get("duration"),
        }

        storage_key = (
            f"telegram:"
            f"{chat['id']}:"
            f"{result['message_id']}"
        )

        return StorageUploadResult(
            storage_key=storage_key,
            metadata=metadata,
        )