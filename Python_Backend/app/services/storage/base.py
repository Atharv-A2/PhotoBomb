from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import AsyncGenerator


class StorageProvider(
    ABC,
):

    @abstractmethod
    def upload_file(
        self,
        path: Path,
        media_type,
    ):
        pass

    @abstractmethod
    async def stream_file(
        self,
        storage_metadata: dict,
        byte_range,
    ) -> AsyncGenerator[
        bytes,
        None,
    ]:
        """
        Stream a byte range from the underlying provider.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_file(
        self,
        storage_metadata: dict,
    ):
        pass

    @abstractmethod
    def download_to_path(
        self,
        storage_metadata: dict,
        destination: Path,
    ):
        raise NotImplementedError

    @abstractmethod
    def shutdown(
        self,
    ):
        pass


    @abstractmethod
    def download_file(
        self,
        storage_metadata,
    ):
        pass