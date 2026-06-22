from pathlib import Path
import aiofiles
from fastapi import UploadFile


class TemporaryStorageService:

    CHUNK_SIZE = (
        1024 * 1024
    )

    async def save(
        self,
        file: UploadFile,
        destination: Path,
    ):
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            async with aiofiles.open(destination, "wb") as output:
                while True:
                    chunk = await file.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    await output.write(chunk)

        except Exception:
            if destination.exists():
                destination.unlink()

            raise

        finally:
            await file.close()