from app.db.models.media import Media


class MediaRepository:

    def __init__(
        self,
        session,
    ):
        self.session = session

    async def create(
        self,
        media: Media,
    ):
        self.session.add(
            media
        )

        await self.session.flush()

        return media