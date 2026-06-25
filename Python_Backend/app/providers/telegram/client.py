from pathlib import Path

import httpx

from app.core.config.settings import (
    get_settings,
)

settings = get_settings()


class TelegramClient:

    def __init__(self):
        self.client = httpx.Client(
            timeout=300,
        )

        self.base_url = (
            f"{settings.telegram_api_base}"
            f"/bot"
            f"{settings.telegram_bot_token}"
        )

    def send_document(
        self,
        chat_id: str,
        path: Path,
    ):
        with open(
            path,
            "rb",
        ) as file:

            response = (
                self.client.post(
                    f"{self.base_url}/sendDocument",
                    data={
                        "chat_id": chat_id,
                    },
                    files={
                        "document": file,
                    },
                )
            )

        response.raise_for_status()

        payload = response.json()

        if not payload["ok"]:
            raise RuntimeError(
                payload
            )

        return payload["result"]

    def get_file(
        self,
        file_id: str,
    ):
        response = self.client.get(
            f"{self.base_url}/getFile",
            params={
                "file_id": file_id,
            },
        )

        response.raise_for_status()

        payload = response.json()

        if not payload["ok"]:
            raise RuntimeError(
                payload
            )

        return payload["result"]
    

    def build_download_url(
        self,
        file_path: str,
    ):
        return (
            f"{settings.telegram_api_base}"
            f"/file/bot"
            f"{settings.telegram_bot_token}"
            f"/{file_path}"
        )


    def download_bytes(
        self,
        file_path: str,
    ):
        url = (
            self.build_download_url(
                file_path
            )
        )

        response = (
            self.client.get(
                url
            )
        )

        response.raise_for_status()

        return response.content


    def stream_file(
        self,
        file_path: str,
    ):
        url = self.build_download_url(
            file_path
        )

        request = self.client.build_request(
            "GET",
            url,
        )

        response = self.client.send(
            request,
            stream=True,
        )

        response.raise_for_status()

        return response