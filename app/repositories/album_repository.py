"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
from app.models.album_model import Album
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps
from app.errors import E
from app.config import get_cfg
import time
import os

cfg = get_cfg()


class AlbumRepository:
    """User repository."""

    def __init__(self, session, cache) -> None:
        """Init User Repository."""
        self.session = session
        self.cache = cache

    async def insert(self, user_id: int, album_name: str, album_summary: str = None):
        """Insert a new album."""
        entity_manager = EntityManager(self.session)

        album = Album(user_id, album_name, album_summary)
        await entity_manager.insert(album, commit=True)

        # TODO: update cache only on entity selection
        # cache_manager = CacheManager(self.cache)
        # await cache_manager.set(album)

        return album

    async def select(self, album_id: int):
        """Select user."""
        cache_manager = CacheManager(self.cache)
        album = await cache_manager.get(Album, album_id)

        if not album:
            entity_manager = EntityManager(self.session)
            album = await entity_manager.select(Album, album_id)

        if not album:
            raise HTTPException(status_code=404)

        await cache_manager.set(album)
        return album

    async def update(self, album: Album, album_name: str, album_summary: str = None):
        """Update album."""
        album.album_name = album_name
        album.album_summary = album_summary
        
        entity_manager = EntityManager(self.session)
        await entity_manager.update(album, commit=True)

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(album)

    async def delete(self, album: Album):
        """Delete album."""
        entity_manager = EntityManager(self.session)
        try:
            await entity_manager.delete(album, commit=True)
        except Exception:
            raise RequestValidationError({"loc": ["path", "user_id"], "input": album.id,
                                         "type": "value_locked", "msg": E.VALUE_LOCKED})

        cache_manager = CacheManager(self.cache)
        await cache_manager.delete(album)

    async def select_all(self, **kwargs):
        """Select all users."""
        entity_manager = EntityManager(self.session)
        albums = await entity_manager.select_all(Album, **kwargs)

        cache_manager = CacheManager(self.cache)
        for album in albums:
            await cache_manager.set(album)
        return albums

    async def count_all(self, **kwargs):
        """Count users."""
        entity_manager = EntityManager(self.session)
        albums_count = await entity_manager.count_all(Album, **kwargs)
        return albums_count
