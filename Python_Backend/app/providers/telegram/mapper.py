from __future__ import annotations

from app.providers.telegram.models import (
    TelegramMedia,
)

from app.services.storage.models import (
    StorageUploadResult,
)


class TelegramMapper:

    @staticmethod
    def to_upload_result(
        media: TelegramMedia,
    ) -> StorageUploadResult:
        """
        Convert Telegram transport media into the generic
        storage upload result.
        """

        return StorageUploadResult(

            storage_key=(
                f"telegram:{media.chat_id}:{media.message_id}"
            ),

            metadata={

                "chat_id": media.chat_id,

                "message_id": media.message_id,

                "file_size": media.file_size,

                "mime_type": media.mime_type,

                "filename": media.filename,
            },
        )

    @staticmethod
    def from_storage(
        metadata: dict,
    ) -> TelegramMedia:
        """
        Reconstruct a TelegramMedia descriptor from the
        stored provider metadata.
        """

        try: 
            return TelegramMedia(

                chat_id=int(
                    metadata["chat_id"]
                ),

                message_id=int(
                    metadata["message_id"]
                ),

                file_size=int(
                    metadata["file_size"]
                ),

                mime_type=metadata.get(
                    "mime_type"
                ),

                filename=metadata.get(
                    "filename"
                ),
            )
        
        except KeyError as exc:
            raise ValueError(
                f"Missing Telegram storage metadata: {exc}"
            )