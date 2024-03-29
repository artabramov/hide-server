"""Mediafile repository."""

from app.managers.file_manager import FileManager
from app.managers.image_manager import ImageManager
from app.models.mediafile_model import Mediafile
from app.models.metadata_model import Metadata
from app.models.colorset_model import Colorset
from app.models.tag_model import Tag, MediafileTag
from app.models.favorite_model import Favorite
from app.helpers.tag_helper import TagHelper
from app.repositories.primary_repository import PrimaryRepository
from fastapi import UploadFile
import uuid
import os
from app.config import get_cfg
import asyncio

cfg = get_cfg()


class MediafileRepository(PrimaryRepository):
    """Mediafile repository."""

    async def _get_mimetype(self, path: str) -> str:
        """Get file mimetype."""
        return FileManager.get_mimetype(path)

    async def _get_filesize(self, path: str) -> int:
        """Get file size."""
        return FileManager.get_filesize(path)

    async def _create_thumbnail(self, mediafile: Mediafile):
        """Create thumbnail."""
        await FileManager.file_copy(mediafile.mediafile_path, mediafile.thumbnail_path)
        ImageManager.create_thumbnail(mediafile.thumbnail_path)

    async def _create_colorset(self, mediafile: Mediafile):
        """Extract and insert colorset."""
        try:
            mediafile_colors = ImageManager.get_colors(mediafile.mediafile_image)
            colorset = Colorset(mediafile.id, **mediafile_colors)
            await self.entity_manager.insert(colorset, flush=False)
        except Exception:
            pass

    async def _create_metadata(self, mediafile: Mediafile):
        """Parse and insert metadata."""
        try:
            metadatas = FileManager.get_metadata(mediafile.mediafile_image)
            for meta_key in metadatas:
                metadata = Metadata(mediafile.id, meta_key, str(metadatas[meta_key]))
                await self.entity_manager.insert(metadata, flush=False)
        except Exception:
            pass

    async def _create_tags(self, mediafile: Mediafile):
        """Parse description and insert tags."""
        if mediafile.mediafile_description:
            tag_values = TagHelper.get_tags(mediafile.mediafile_description)
            for tag_value in tag_values:
                tag = await self.entity_manager.select_by(Tag, tag_value__eq=tag_value)
                if not tag:
                    tag = Tag(tag_value)
                    await self.entity_manager.insert(tag)

                mediafile_tag = MediafileTag(mediafile.id, tag.id)
                await self.entity_manager.insert(mediafile_tag, flush=False)

    async def _delete_tags(self, mediafile: Mediafile):
        """Delete mediafile tags."""
        # __dict__ checking is mandatory for cases when SQLAlchemy relationship
        # is not loaded yet (transaction rollback on mediafile uploading)
        if "mediafile_tags" in mediafile.__dict__:
            for tag in mediafile.mediafile_tags:
                mediafile_tag = await self.entity_manager.select_by(MediafileTag, mediafile_id__eq=mediafile.id, tag_id__eq=tag.id)
                await self.entity_manager.delete(mediafile_tag)

                tag_used = await self.entity_manager.count_all(MediafileTag, mediafile_id__not=mediafile.id, tag_id__eq=tag.id)
                if not tag_used:
                    await self.entity_manager.delete(tag)

    async def insert(self, file: UploadFile, user_id: int, album_id: int, mediafile_description: str=None,
                     commit: bool=False) -> Mediafile:
        """Upload mediafile."""
        try:
            mediafile_path, thumbnail_path = None, None

            # upload file
            mediafile_filename = str(uuid.uuid4())
            mediafile_path = os.path.join(cfg.MEDIAFILE_PATH, mediafile_filename)
            await FileManager.file_upload(file, mediafile_path)

            # get file properties
            funcs = [self._get_mimetype, self._get_filesize]
            tasks = [asyncio.create_task(func(mediafile_path)) for func in funcs]
            mimetype, filesize = await asyncio.gather(*tasks)

            # will create thumbnail later in async task
            thumbnail_filename = str(uuid.uuid4()) + cfg.THUMBNAIL_EXTENSION
            thumbnail_path = os.path.join(cfg.THUMBNAIL_PATH, thumbnail_filename)

            # create mediafile
            mediafile = Mediafile(user_id, album_id, file.filename, mediafile_filename, thumbnail_filename,
                                mimetype, filesize, mediafile_description=mediafile_description)
            await self.entity_manager.insert(mediafile)

            # create related data
            funcs = [self._create_thumbnail, self._create_colorset, self._create_metadata, self._create_tags]
            tasks = [asyncio.create_task(func(mediafile)) for func in funcs]
            await asyncio.gather(*tasks)

            # encrypt original file
            await mediafile.encrypt()

        except Exception:
            if mediafile_path:
                await FileManager.file_delete(mediafile_path)

            if thumbnail_path:
                await FileManager.file_delete(thumbnail_path)

            raise

        if commit:
            await self.entity_manager.commit()

        return mediafile

    async def select(self, mediafile_id: int) -> Mediafile | None:
        """Select mediafile."""
        mediafile = await self.cache_manager.get(Mediafile, mediafile_id)
        if not mediafile:
            mediafile = await self.entity_manager.select(Mediafile, mediafile_id)

        if mediafile:
            await self.cache_manager.set(mediafile)
            return mediafile

    async def update(self, mediafile: Mediafile, commit: bool=False):
        """Update mediafile."""
        await self.entity_manager.update(mediafile)
        await self._delete_tags(mediafile)
        await self._create_tags(mediafile)

        if commit:
            await self.entity_manager.commit()

        await self.cache_manager.delete(mediafile)

    async def delete(self, mediafile: Mediafile, commit: bool=False):
        """Delete mediafile."""
        paths = [mediafile.mediafile_path, mediafile.thumbnail_path]
        tasks = [asyncio.create_task(FileManager.file_delete(path)) for path in paths]
        await asyncio.gather(*tasks)

        await self.entity_manager.delete(mediafile)
        await self._delete_tags(mediafile)

        if commit:
            await self.entity_manager.commit()

        await self.cache_manager.delete(mediafile)

    async def select_all(self, **kwargs) -> list[Mediafile]:
        """Select mediafiles."""
        mediafiles = await self.entity_manager.select_all(Mediafile, **kwargs)
        for mediafile in mediafiles:
            await self.cache_manager.set(mediafile)
        return mediafiles

    async def count_all(self, **kwargs) -> int:
        """Count mediafiles."""
        return await self.entity_manager.count_all(Mediafile, **kwargs)

    async def sum_all(self, column: str, **kwargs) -> int:
        """Sum mediafiles column."""
        return await self.entity_manager.sum_all(Mediafile, column, **kwargs)

    async def lock_all(self):
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


