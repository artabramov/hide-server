"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
from app.managers.image_manager import ImageManager
from app.models.user_model import User
from app.models.album_model import Album
from app.models.mediafile_model import Mediafile
from app.models.metaparam_model import Metaparam
from app.models.colormap_model import Colormap
from app.models.tag_model import Tag, MediafileTag
from app.helpers.jwt_helper import JWTHelper
from app.helpers.mfa_helper import MFAHelper
from app.helpers.hash_helper import HashHelper
from app.helpers.tag_helper import TagHelper
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps
from app.errors import E
from app.config import get_cfg
import time
import os

cfg = get_cfg()


class MediafileRepository:
    """User repository."""

    def __init__(self, session, cache) -> None:
        """Init User Repository."""
        self.session = session
        self.cache = cache

    async def upload(self, user: User, album: Album, file: UploadFile):
        """Upload userpic."""
        if file.content_type not in cfg.MEDIAFILE_MIMES:
            raise RequestValidationError({"loc": ["file", "file"], "input": file.content_type,
                                          "type": "file_mime", "msg": E.FILE_MIME_INVALID})
        
        original_filename = file.filename
        mediafile_summary = None

        filename = await FileManager.file_upload(file, cfg.MEDIAFILE_PATH)
        mediafile_path = os.path.join(cfg.MEDIAFILE_PATH, filename)
        mimetype = FileManager.get_mimetype(mediafile_path)
        filesize = FileManager.get_filesize(mediafile_path)

        im = Image.open(mediafile_path)
        width = im.width
        height = im.height
        format = im.format
        mode = im.mode

        thumbnail = await FileManager.file_copy(mediafile_path, cfg.THUMBNAIL_PATH)
        thumbnail_path = os.path.join(cfg.THUMBNAIL_PATH, thumbnail)

        thumbnail_image = Image.open(thumbnail_path)
        thumbnail_image.thumbnail(tuple([cfg.THUMBNAIL_WIDTH, cfg.THUMBNAIL_HEIGHT]))
        thumbnail_image.save(thumbnail_path, image_quality=cfg.THUMBNAIL_QUALITY)

        entity_manager = EntityManager(self.session)

        mediafile = Mediafile(user.id, album.id, original_filename, filename, filesize, width, height, mimetype, format, mode,
                              thumbnail, mediafile_summary=None)
        await entity_manager.insert(mediafile, commit=True)

        metaparams = FileManager.get_metaparams(im)
        for meta_key in metaparams:
            metaparam = Metaparam(mediafile.id, meta_key, str(metaparams[meta_key]))
            await entity_manager.insert(metaparam, commit=True)
        
        mediafile_colors = ImageManager.get_colors(im)
        colormap = Colormap(mediafile.id, **mediafile_colors)
        await entity_manager.insert(colormap, commit=True)
        pass

        album.mediafiles_size = await entity_manager.sum_all(Mediafile, "filesize", album_id__eq=album.id)
        album.mediafiles_count = await entity_manager.count_all(Mediafile, album_id__eq=album.id)
        await entity_manager.update(album, commit=True)

        return mediafile

    async def select(self, mediafile_id: int):
        """Select user."""
        cache_manager = CacheManager(self.cache)
        mediafile = await cache_manager.get(Mediafile, mediafile_id)

        if not mediafile:
            entity_manager = EntityManager(self.session)
            mediafile = await entity_manager.select(Mediafile, mediafile_id)

        if not mediafile:
            raise HTTPException(status_code=404)

        await cache_manager.set(mediafile)
        return mediafile

    async def update(self, mediafile: Mediafile, album: Album, original_filename: str, mediafile_summary: str = None):
        """Update album."""
        outdated_album_id = mediafile.album_id if mediafile.album_id != album.id else None

        mediafile.album_id = album.id
        mediafile.original_filename = original_filename
        mediafile.mediafile_summary = mediafile_summary
        
        entity_manager = EntityManager(self.session)
        await entity_manager.update(mediafile)

        if outdated_album_id:
            outdated_album = await entity_manager.select(Album, outdated_album_id)
            outdated_album.mediafiles_size = await entity_manager.sum_all(Mediafile, "filesize", album_id__eq=outdated_album_id)
            outdated_album.mediafiles_count = await entity_manager.count_all(Mediafile, album_id__eq=outdated_album_id)
            await entity_manager.update(outdated_album)

            album = await entity_manager.select(Album, album.id)
            album.mediafiles_size = await entity_manager.sum_all(Mediafile, "filesize", album_id__eq=album.id)
            album.mediafiles_count = await entity_manager.count_all(Mediafile, album_id__eq=album.id)
            await entity_manager.update(album)

        await entity_manager.commit()

        # tags
        if mediafile_summary:
            tag_values = TagHelper.get_tags(mediafile_summary)
            for tag_value in tag_values:
                pass
                # tag = Tag(tag_value)
                # await entity_manager.insert(tag)

                # mediafile_tag = MediafileTag(mediafile.id, tag.id)
                # await entity_manager.insert(mediafile_tag)

                # await entity_manager.commit()

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(mediafile)

    async def delete(self, mediafile: Mediafile):
        """Delete a media."""
        mediafile_path = os.path.join(cfg.MEDIAFILE_PATH, mediafile.filename)
        FileManager.file_delete(mediafile_path)

        entity_manager = EntityManager(self.session)
        await entity_manager.delete(mediafile, commit=True)

        album = await entity_manager.select(Album, mediafile.album_id)
        album.mediafiles_size = await entity_manager.sum_all(Mediafile, "filesize", album_id__eq=album.id)
        album.mediafiles_count = await entity_manager.count_all(Mediafile, album_id__eq=album.id)
        await entity_manager.update(album, commit=True)

        cache_manager = CacheManager(self.cache)
        await cache_manager.delete(mediafile)

    async def select_all(self, **kwargs):
        """Select all users."""
        entity_manager = EntityManager(self.session)
        mediafiles = await entity_manager.select_all(Mediafile, **kwargs)

        cache_manager = CacheManager(self.cache)
        for mediafile in mediafiles:
            await cache_manager.set(mediafile)
        return mediafiles

    async def count_all(self, **kwargs):
        """Count users."""
        entity_manager = EntityManager(self.session)
        mediafiles_count = await entity_manager.count_all(Mediafile, **kwargs)
        return mediafiles_count
