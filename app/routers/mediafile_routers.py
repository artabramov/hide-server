from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.mediafile_schemas import MediafileSchema, MediafileInsertSchema, MediafileUpdateSchema, MediafilesListSchema
from app.repositories.album_repository import AlbumRepository
from app.repositories.mediafile_repository import MediafileRepository
from app.repositories.comment_repository import CommentRepository
from app.auth import auth_admin, auth_editor, auth_writer, auth_reader
from app.errors import E
from app.config import get_cfg
import os

cfg = get_cfg()
router = APIRouter()


@router.post('/mediafile', tags=['mediafiles'])
async def upload_mediafile(session = Depends(get_session), cache = Depends(get_cache),
                           schema = Depends(MediafileInsertSchema), current_user=Depends(auth_writer)):
    """Upload mediafile."""
    if schema.file.content_type not in cfg.MEDIAFILE_MIMES:
        raise HTTPException(status_code=415)

    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(schema.album_id)
    if not album:
        raise RequestValidationError({"loc": ["query", "album_id"], "input": schema.album_id,
                                      "type": "value_invalid", "msg": E.VALUE_INVALID})
    
    elif album.is_locked:
        raise RequestValidationError({"loc": ["query", "album_id"], "input": schema.album_id,
                                      "type": "value_locked", "msg": E.VALUE_LOCKED})

    mediafile_repository = MediafileRepository(session, cache)
    await mediafile_repository.lock_all()
    mediafile = await mediafile_repository.insert(schema.file, current_user.id, album.id,
                                                  mediafile_description=schema.mediafile_description)

    try:
        album.mediafiles_count = await mediafile_repository.count_all(album_id__eq=album.id)
        album.mediafiles_size = await mediafile_repository.sum_all("filesize", album_id__eq=album.id)
        await album_repository.update(album)
    except Exception:
        await mediafile_repository.delete(mediafile)
        raise

    return {
        "mediafile_id": mediafile.id,
    }


@router.get('/mediafile/{mediafile_id}', tags=['mediafiles'], response_model=MediafileSchema)
async def select_mediafile(mediafile_id: int, session = Depends(get_session), cache = Depends(get_cache),
                           current_user=Depends(auth_reader)):
    """Select mediafile."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(mediafile_id)
    if not mediafile:
        raise HTTPException(status_code=404)

    return mediafile.to_dict()


@router.put('/mediafile/{mediafile_id}', tags=['mediafiles'])
async def update_mediafile(mediafile_id: int, session = Depends(get_session), cache = Depends(get_cache),
                           schema = Depends(MediafileUpdateSchema), current_user=Depends(auth_editor)):
    """Update mediafile."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(mediafile_id)
    if not mediafile:
        raise HTTPException(status_code=404)

    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(schema.album_id)
    if not album:
        raise RequestValidationError({"loc": ["query", "album_id"], "input": schema.album_id,
                                      "type": "value_invalid", "msg": E.VALUE_INVALID})

    elif album.is_locked:
        raise RequestValidationError({"loc": ["query", "album_id"], "input": schema.album_id,
                                      "type": "value_locked", "msg": E.VALUE_LOCKED})
    
    mediafile.album_id = album.id
    mediafile.original_filename = schema.original_filename
    mediafile.mediafile_description = schema.mediafile_description

    await mediafile_repository.lock_all()
    await mediafile_repository.update(mediafile)

    if mediafile.mediafile_album.id != mediafile.album_id:
        mediafile.mediafile_album.mediafiles_count = await mediafile_repository.count_all(album_id__eq=mediafile.mediafile_album.id)
        mediafile.mediafile_album.mediafiles_size = await mediafile_repository.sum_all("filesize", album_id__eq=mediafile.mediafile_album.id)
        await album_repository.update(mediafile.mediafile_album)

        album.mediafiles_count = await mediafile_repository.count_all(album_id__eq=album.id)
        album.mediafiles_size = await mediafile_repository.sum_all("filesize", album_id__eq=album.id)
        await album_repository.update(album)
    return {}


@router.delete('/mediafile/{mediafile_id}', tags=['mediafiles'])
async def delete_mediafile(mediafile_id: int, session=Depends(get_session), cache=Depends(get_cache),
                           current_user=Depends(auth_editor)):
    """Delete mediafile."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(mediafile_id)
    if not mediafile:
        raise HTTPException(status_code=404)

    await mediafile_repository.delete(mediafile)
    
    comment_repository = CommentRepository(session, cache)
    await comment_repository.delete_all(mediafile_id__eq=mediafile.id)

    album_repository = AlbumRepository(session, cache)
    mediafile.mediafile_album.mediafiles_count = await mediafile_repository.count_all(album_id__eq=mediafile.mediafile_album.id, id__not=mediafile.id)
    mediafile.mediafile_album.mediafiles_size = await mediafile_repository.sum_all("filesize", album_id__eq=mediafile.mediafile_album.id, id__not=mediafile.id)
    await album_repository.update(mediafile.mediafile_album)

    return {}

@router.get('/mediafiles', tags=['mediafiles'])
async def mediafiles_list(session = Depends(get_session), cache = Depends(get_cache),
                          schema = Depends(MediafilesListSchema), current_user=Depends(auth_reader)):
    """Get users list."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafiles = await mediafile_repository.select_all(**schema.kwargs)
    mediafiles_count = await mediafile_repository.count_all(**schema.kwargs)
    return {
        "mediafiles": [mediafile.to_dict() for mediafile in mediafiles],
        "mediafiles_count": mediafiles_count,
    }
