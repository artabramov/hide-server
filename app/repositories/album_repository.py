"""User repository."""

from app.repositories.base_repository import BaseRepository
from app.models.album_model import Album


class AlbumRepository(BaseRepository):
    """Album repository."""

    async def insert(self, album: Album, commit: bool=False) -> Album:
        """Insert album."""
        await self.entity_manager.insert(album, commit=commit)
        return album

    async def select(self, album_id: int) -> Album:
        """Select album."""
        album = await self.cache_manager.get(Album, album_id)
        if not album:
            album = await self.entity_manager.select(Album, album_id)

        if not album:
            raise ValueError

        await self.cache_manager.set(album)
        return album

    async def update(self, album: Album, commit: bool=False) -> Album:
        """Update album."""
        await self.entity_manager.update(album, commit=commit)
        await self.cache_manager.delete(album)
        return album

    async def delete(self, album: Album, commit: bool=False) -> None:
        """Delete album."""
        await self.entity_manager.delete(album, commit=commit)
        await self.cache_manager.delete(album)

    async def select_all(self, **kwargs):
        """Select albums."""
        albums = await self.entity_manager.select_all(Album, **kwargs)
        for album in albums:
            await self.cache_manager.set(album)
        return albums

    async def count_all(self, **kwargs):
        """Count albums."""
        return await self.entity_manager.count_all(Album, **kwargs)
