from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.mediafile_schemas import MediafileUploadSchema, MediafileUpdateSchema, MediafilesListSchema
from app.repositories.album_repository import AlbumRepository
from app.repositories.mediafile_repository import MediafileRepository
from app.auth import auth_admin, auth_editor, auth_writer, auth_reader
from app.errors import E

router = APIRouter()


@router.post('/mediafile', tags=['mediafiles'])
async def upload_mediafile(session = Depends(get_session), cache = Depends(get_cache),
                           schema = Depends(MediafileUploadSchema), current_user=Depends(auth_writer)):
    """Upload userpic."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(schema.album_id)

    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.upload(current_user, album, schema.file,
                                                  mediafile_description=schema.mediafile_description)
    return {"mediafile_id": mediafile.id}


@router.get('/mediafile/{mediafile_id}', tags=['mediafiles'])
async def select_mediafile(mediafile_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       current_user=Depends(auth_reader)):
    """Select an album."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(mediafile_id)
    return mediafile.to_dict()


@router.put('/mediafile/{mediafile_id}', tags=['mediafiles'])
async def update_mediafile(mediafile_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       schema = Depends(MediafileUpdateSchema), current_user=Depends(auth_editor)):
    """Update album."""
    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(mediafile_id)
    
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
