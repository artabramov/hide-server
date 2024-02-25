"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
from app.managers.image_manager import ImageManager
from app.models.user_model import User
from app.models.album_model import Album
from app.models.mediafile_model import Mediafile
from app.models.metadata_model import Metadata
from app.models.colorset_model import Colorset
from app.models.tag_model import Tag, MediafileTag
from app.models.favorite_model import Favorite
from app.models.comment_model import Comment
from app.helpers.jwt_helper import JWTHelper
from app.helpers.mfa_helper import MFAHelper
from app.helpers.hash_helper import HashHelper
from app.helpers.tag_helper import TagHelper
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps
from app.repositories.base_repository import BaseRepository
from app.errors import E
from app.config import get_cfg
import time
import os

cfg = get_cfg()


class MediafileRepository(BaseRepository):
    """Mediafile repository."""

    async def insert(self, mediafile: Mediafile, im: Image, commit: bool=False) -> Mediafile:
        """Insert mediafile."""
        await self.entity_manager.insert(mediafile)

        # colorset
        mediafile_colors = ImageManager.get_colors(im)
        colorset = Colorset(mediafile.id, **mediafile_colors)
        await self.entity_manager.insert(colorset)

        # metadata
        metadatas = FileManager.get_metadata(im)
        for meta_key in metadatas:
            metadata = Metadata(mediafile.id, meta_key, str(metadatas[meta_key]))
            await self.entity_manager.insert(metadata)

        # tags
        if mediafile.mediafile_description:
            tag_values = TagHelper.get_tags(mediafile.mediafile_description)
            for tag_value in tag_values:
                tag = await self.entity_manager.select_by(Tag, tag_value__eq=tag_value)
                if not tag:
                    tag = Tag(tag_value)
                    await self.entity_manager.insert(tag)

                mediafile_tag = MediafileTag(mediafile.id, tag.id)
                await self.entity_manager.insert(mediafile_tag)

        if commit:
            await self.entity_manager.commit()

        return mediafile

    async def select(self, mediafile_id: int) -> Mediafile:
        """Select mediafile."""
        mediafile = await self.cache_manager.get(Mediafile, mediafile_id)
        if not mediafile:
            mediafile = await self.entity_manager.select(Mediafile, mediafile_id)

        if not mediafile:
            raise ValueError

        await self.cache_manager.set(mediafile)
        return mediafile

    async def update(self, mediafile: Mediafile, commit: bool=False) -> Mediafile:
        """Update mediafile."""
        await self.entity_manager.update(mediafile, commit=commit)
        await self.cache_manager.delete(mediafile)
        return mediafile

    async def count_all(self, **kwargs) -> int:
        """Count mediafiles."""
        return await self.entity_manager.count_all(Mediafile, **kwargs)

    async def sum_all(self, column: str, **kwargs) -> int:
        """Sum mediafiles column."""
        return await self.entity_manager.sum_all(Mediafile, column, **kwargs)

    async def lock_all(self) -> None:
        """Lock mediafiles."""
        return await self.entity_manager.lock_all(Mediafile)





    # async def update(self, mediafile: Mediafile, album: Album, original_filename: str, mediafile_description: str=None,
    #                  commit: bool=False):
    #     """Update album."""
    #     outdated_album_id = mediafile.album_id if mediafile.album_id != album.id else None

    #     mediafile.album_id = album.id
    #     mediafile.original_filename = original_filename
    #     mediafile.mediafile_description = mediafile_description
        
    #     entity_manager = EntityManager(self.session)
    #     await entity_manager.update(mediafile)

    #     if outdated_album_id:
    #         outdated_album = await entity_manager.select(Album, outdated_album_id)
    #         outdated_album.mediafiles_size = await entity_manager.sum_all(Mediafile, "filesize", album_id__eq=outdated_album_id)
    #         outdated_album.mediafiles_count = await entity_manager.count_all(Mediafile, album_id__eq=outdated_album_id)
    #         await entity_manager.update(outdated_album)

    #         album = await entity_manager.select(Album, album.id)
    #         album.mediafiles_size = await entity_manager.sum_all(Mediafile, "filesize", album_id__eq=album.id)
    #         album.mediafiles_count = await entity_manager.count_all(Mediafile, album_id__eq=album.id)
    #         await entity_manager.update(album)

    #     # tags
    #     # if mediafile_description:
    #     #     tag_values = TagHelper.get_tags(mediafile_description)
    #     #     for tag_value in tag_values:
    #     #         tag = Tag(tag_value)
    #     #         await entity_manager.insert(tag)

    #     #         mediafile_tag = MediafileTag(mediafile.id, tag.id)
    #     #         await entity_manager.insert(mediafile_tag)

    #     #         await entity_manager.commit()
    #     #         pass

    #     if commit:
    #         await entity_manager.commit()

    #     cache_manager = CacheManager(self.cache)
    #     await cache_manager.delete(mediafile)

    # async def delete(self, mediafile: Mediafile):
    #     """Delete a media."""
    #     mediafile_path = os.path.join(cfg.MEDIAFILE_PATH, mediafile.filename)
    #     FileManager.file_delete(mediafile_path)

    #     entity_manager = EntityManager(self.session)
    #     await entity_manager.delete(mediafile, commit=True)

    #     album = await entity_manager.select(Album, mediafile.album_id)
    #     album.mediafiles_size = await entity_manager.sum_all(Mediafile, "filesize", album_id__eq=album.id)
    #     album.mediafiles_count = await entity_manager.count_all(Mediafile, album_id__eq=album.id)
    #     await entity_manager.update(album, commit=True)

    #     cache_manager = CacheManager(self.cache)
    #     await cache_manager.delete(mediafile)

    # async def select_all(self, **kwargs):
    #     """Select all users."""
    #     entity_manager = EntityManager(self.session)
    #     mediafiles = await entity_manager.select_all(Mediafile, **kwargs)

    #     cache_manager = CacheManager(self.cache)
    #     for mediafile in mediafiles:
    #         await cache_manager.set(mediafile)
    #     return mediafiles


