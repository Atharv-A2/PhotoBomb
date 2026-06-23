from pathlib import Path

from PIL import Image


class ImageThumbnailService:

    MAX_SIZE = (
        512,
        512,
    )

    def generate(
        self,
        source: Path,
        destination: Path,
    ):
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with Image.open(
            source
        ) as image:

            image.thumbnail(
                self.MAX_SIZE,
                Image.Resampling.LANCZOS,
            )

            image.save(
                destination,
                format="WEBP",
                quality=80,
            )

        return destination