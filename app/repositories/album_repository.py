"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
from app.models.album_models import Album
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

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(album)

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

    # async def pass_update(self, user: User, user_pass: str, user_pass_new: str):
    #     """Update user password."""
    #     if user.pass_hash != HashHelper.get_hash(user_pass):
    #         raise RequestValidationError({"loc": ["query", "user_pass"], "input": user_pass,
    #                                       "type": "pass_invalid", "msg": E.USER_PASS_INVALID})

    #     user.user_pass = user_pass_new

    #     entity_manager = EntityManager(self.session)
    #     await entity_manager.update(user, commit=True)

    #     cache_manager = CacheManager(self.cache)
    #     await cache_manager.set(user)


    # async def role_update(self, user: User, user_role: str):
    #     """Update user role."""
    #     user.user_role = user_role

    #     entity_manager = EntityManager(self.session)
    #     await entity_manager.update(user, commit=True)

    #     cache_manager = CacheManager(self.cache)
    #     await cache_manager.set(user)


    # async def delete(self, user: User):
    #     """Delete user."""
    #     entity_manager = EntityManager(self.session)
    #     try:
    #         await entity_manager.delete(user, commit=True)
    #     except Exception:
    #         raise RequestValidationError({"loc": ["path", "user_id"], "input": user.id,
    #                                      "type": "value_locked", "msg": E.VALUE_LOCKED})

    #     cache_manager = CacheManager(self.cache)
    #     await cache_manager.delete(user)

    # async def select_all(self, **kwargs):
    #     """Select all users."""
    #     entity_manager = EntityManager(self.session)
    #     users = await entity_manager.select_all(User, **kwargs)

    #     cache_manager = CacheManager(self.cache)
    #     for user in users:
    #         await cache_manager.set(user)
    #     return users

    # async def count_all(self, **kwargs):
    #     """Count users."""
    #     entity_manager = EntityManager(self.session)
    #     users_count = await entity_manager.count_all(User, **kwargs)
    #     return users_count


    # async def userpic_upload(self, user: User, file: UploadFile):
    #     """Upload userpic."""
    #     if file.content_type not in cfg.USERPIC_MIMES:
    #         raise RequestValidationError({"loc": ["file", "file"], "input": file.content_type,
    #                                       "type": "file_mime", "msg": E.FILE_MIME_INVALID})

    #     userpic = await FileManager.file_upload(file, cfg.USERPIC_PATH)
    #     userpic_path = os.path.join(cfg.USERPIC_PATH, userpic)

    #     original_image = Image.open(userpic_path)
    #     userpic_image = ImageOps.fit(original_image, tuple([cfg.USERPIC_WIDTH, cfg.USERPIC_HEIGHT]), Image.LANCZOS)
    #     userpic_image.save(userpic_path, image_quality=cfg.USERPIC_QUALITY)

    #     await self.userpic_delete(user)
    #     user.userpic = userpic

    #     entity_manager = EntityManager(self.session)
    #     await entity_manager.update(user, commit=True)

    #     cache_manager = CacheManager(self.cache)
    #     await cache_manager.set(user)

    # async def userpic_delete(self, user: User):
    #     """Delete userpic."""
    #     if user.userpic:
    #         userpic_path = os.path.join(cfg.USERPIC_PATH, user.userpic)
    #         await FileManager.file_delete(userpic_path)

    #         user.userpic = None

    #         entity_manager = EntityManager(self.session)
    #         await entity_manager.update(user, commit=True)

    #         cache_manager = CacheManager(self.cache)
    #         await cache_manager.set(user)
