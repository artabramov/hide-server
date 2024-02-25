from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.mediafile_schemas import MediafileUploadSchema, MediafileUpdateSchema, MediafilesListSchema
from app.repositories.album_repository import AlbumRepository
from app.repositories.mediafile_repository import MediafileRepository
from app.auth import auth_admin, auth_editor, auth_writer, auth_reader
from app.managers.file_manager import FileManager
from app.managers.image_manager import ImageManager
from PIL import Image, ImageOps
from app.models.mediafile_model import Mediafile
from app.errors import E
from app.config import get_cfg
import os

router = APIRouter()
cfg = get_cfg()


@router.post('/mediafile', tags=['mediafiles'])
async def upload_mediafile(session = Depends(get_session), cache = Depends(get_cache),
                           schema = Depends(MediafileUploadSchema), current_user=Depends(auth_writer)):
    """Upload mediafile."""
    if schema.file.content_type not in cfg.MEDIAFILE_MIMES:
        raise HTTPException(status_code=415)

    try:
        album_repository = AlbumRepository(session, cache)
        album = await album_repository.select(schema.album_id)
    except ValueError:
        raise RequestValidationError({"loc": ["query", "album_id"], "input": schema.album_id,
                                      "type": "value_invalid", "msg": E.VALUE_INVALID})
    
    try:
        mediafile_filename = await FileManager.file_upload(schema.file, cfg.MEDIAFILE_PATH)
        mediafile_path = os.path.join(cfg.MEDIAFILE_PATH, mediafile_filename)

        thumbnail_filename = await FileManager.file_copy(mediafile_path, cfg.THUMBNAIL_PATH)
        thumbnail_path = os.path.join(cfg.THUMBNAIL_PATH, thumbnail_filename)
        ImageManager.create_thumbnail(thumbnail_path)

        mimetype = FileManager.get_mimetype(mediafile_path)
        filesize = FileManager.get_filesize(mediafile_path)
        im = ImageManager.open_image(mediafile_path)
        mediafile = Mediafile(current_user.id, album.id, schema.file.filename, mediafile_filename, filesize, im.width,
                              im.height, mimetype, im.format, im.mode, thumbnail_filename,
                              mediafile_description=schema.mediafile_description)
        
        mediafile_repository = MediafileRepository(session, cache)
        await mediafile_repository.lock_all()
        await mediafile_repository.insert(mediafile, im)

    except Exception as e:
        if mediafile_path:
            await FileManager.file_delete(mediafile_path)

        if thumbnail_path:
            await FileManager.file_delete(thumbnail_path)

        raise e

    album.mediafiles_count = await mediafile_repository.count_all(album_id__eq=album.id)
    album.mediafiles_size = await mediafile_repository.sum_all("filesize", album_id__eq=album.id)
    await mediafile_repository.update(album, commit=True)

    return {
        "mediafile_id": mediafile.id,
    }


@router.get('/mediafile/{mediafile_id}', tags=['mediafiles'])
async def select_mediafile(mediafile_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       current_user=Depends(auth_reader)):
    """Select mediafile."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(mediafile_id)
    return mediafile.to_dict()


@router.put('/mediafile/{mediafile_id}', tags=['mediafiles'])
async def update_mediafile(mediafile_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       schema = Depends(MediafileUpdateSchema), current_user=Depends(auth_editor)):
    """Update mediafile."""
    try:
        mediafile_repository = MediafileRepository(session, cache)
        mediafile = await mediafile_repository.select(mediafile_id)
    except ValueError:
        raise HTTPException(status_code=404)

    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(schema.album_id)

    await mediafile_repository.update(mediafile, album, schema.original_filename, mediafile_description=schema.mediafile_description)
    return {}


@router.delete('/mediafile/{mediafile_id}', tags=['mediafiles'])
async def delete_mediafile(mediafile_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       current_user=Depends(auth_admin)):
    """Delete media."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(mediafile_id)

    await mediafile_repository.delete(mediafile)
    return {}

@router.get('/mediafiles', tags=['mediafiles'])
async def mediafiles_list(session = Depends(get_session), cache = Depends(get_cache),
                     schema = Depends(MediafilesListSchema), current_user=Depends(auth_reader)):
    """Get users list."""
    mediafile_repository = MediafileRepository(session, cache)

    kwargs = {key[0]: key[1] for key in schema if key[1]}
    mediafiles = await mediafile_repository.select_all(**kwargs)
    mediafiles_count = await mediafile_repository.count_all(**kwargs)
    return {
        "mediafiles": [mediafile.to_dict() for mediafile in mediafiles],
        "mediafiles_count": mediafiles_count,
    }
