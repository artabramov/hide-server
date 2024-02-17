"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
from app.models.user_model import User
from app.models.album_model import Album
from app.models.media_model import Media
from app.models.exif_model import Exif
from app.helpers.jwt_helper import JWTHelper
from app.helpers.mfa_helper import MFAHelper
from app.helpers.hash_helper import HashHelper
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps
from app.errors import E
from app.config import get_cfg
import time
import os

cfg = get_cfg()


class MediaRepository:
    """User repository."""

    def __init__(self, session, cache) -> None:
        """Init User Repository."""
        self.session = session
        self.cache = cache

    async def upload(self, user: User, album: Album, file: UploadFile):
        """Upload userpic."""
        if file.content_type not in cfg.MEDIA_MIMES:
            raise RequestValidationError({"loc": ["file", "file"], "input": file.content_type,
                                          "type": "file_mime", "msg": E.FILE_MIME_INVALID})
        
        media_name = file.filename
        media_summary = None

        filename = await FileManager.file_upload(file, cfg.MEDIA_PATH)
        media_path = os.path.join(cfg.MEDIA_PATH, filename)
        mimetype = FileManager.get_mimetype(media_path)
        filesize = FileManager.get_filesize(media_path)

        im = Image.open(media_path)
        width = im.width
        height = im.height
        format = im.format
        mode = im.mode

        thumbnail = await FileManager.file_copy(media_path, cfg.THUMBNAIL_PATH)
        thumbnail_path = os.path.join(cfg.THUMBNAIL_PATH, thumbnail)

        thumbnail_image = Image.open(thumbnail_path)
        thumbnail_image.thumbnail(tuple([cfg.THUMBNAIL_WIDTH, cfg.THUMBNAIL_HEIGHT]))
        thumbnail_image.save(thumbnail_path, image_quality=cfg.THUMBNAIL_QUALITY)

        entity_manager = EntityManager(self.session)

        media = Media(user.id, album.id, media_name, filename, filesize, width, height, mimetype, format, mode,
                      thumbnail, media_summary=None)
        await entity_manager.insert(media, commit=True)

        media_exif = FileManager.get_exif(im)
        for exif_key in media_exif:
            exif = Exif(media.id, exif_key, str(media_exif[exif_key]))
            await entity_manager.insert(exif, commit=True)

        album.media_size = await entity_manager.sum_all(Media, "filesize", album_id__eq=album.id)
        album.media_count = await entity_manager.count_all(Media, album_id__eq=album.id)
        await entity_manager.update(album, commit=True)

        return media

    async def select(self, media_id: int):
        """Select user."""
        cache_manager = CacheManager(self.cache)
        media = await cache_manager.get(Media, media_id)

        if not media:
            entity_manager = EntityManager(self.session)
            media = await entity_manager.select(Media, media_id)

        if not media:
            raise HTTPException(status_code=404)

        await cache_manager.set(media)
        return media

    async def update(self, media: Media, album: Album, media_name: str, media_summary: str = None):
        """Update album."""
        outdated_album_id = media.album_id if media.album_id != album.id else None

        media.album_id = album.id
        media.media_name = media_name
        media.media_summary = media_summary
        
        entity_manager = EntityManager(self.session)
        await entity_manager.update(media)

        if outdated_album_id:
            outdated_album = await entity_manager.select(Album, outdated_album_id)
            outdated_album.media_size = await entity_manager.sum_all(Media, "filesize", album_id__eq=outdated_album_id)
            outdated_album.media_count = await entity_manager.count_all(Media, album_id__eq=outdated_album_id)
            await entity_manager.update(outdated_album)

            album = await entity_manager.select(Album, album.id)
            album.media_size = await entity_manager.sum_all(Media, "filesize", album_id__eq=album.id)
            album.media_count = await entity_manager.count_all(Media, album_id__eq=album.id)
            await entity_manager.update(album)

        await entity_manager.commit()

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(media)

    async def delete(self, media: Media):
        """Delete a media."""
        media_path = os.path.join(cfg.MEDIA_PATH, media.filename)
        FileManager.file_delete(media_path)

        entity_manager = EntityManager(self.session)
        await entity_manager.delete(media, commit=True)

        album = await entity_manager.select(Album, media.album_id)
        album.media_size = await entity_manager.sum_all(Media, "filesize", album_id__eq=album.id)
        album.media_count = await entity_manager.count_all(Media, album_id__eq=album.id)
        await entity_manager.update(album, commit=True)

        cache_manager = CacheManager(self.cache)
        await cache_manager.delete(media)

    async def select_all(self, **kwargs):
        """Select all users."""
        entity_manager = EntityManager(self.session)
        medias = await entity_manager.select_all(Media, **kwargs)

        cache_manager = CacheManager(self.cache)
        for media in medias:
            await cache_manager.set(media)
        return medias

    async def count_all(self, **kwargs):
        """Count users."""
        entity_manager = EntityManager(self.session)
        medias_count = await entity_manager.count_all(Media, **kwargs)
        return medias_count
