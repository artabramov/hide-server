from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.media_schemas import MediaUploadSchema, MediaUpdateSchema, MediaListSchema
from app.repositories.album_repository import AlbumRepository
from app.repositories.media_repository import MediaRepository
from app.auth import auth_admin, auth_editor, auth_writer, auth_reader
from app.errors import E

router = APIRouter()


@router.post('/media', tags=['media'])
async def upload_media(session = Depends(get_session), cache = Depends(get_cache),
                         schema = Depends(MediaUploadSchema), current_user=Depends(auth_writer)):
    """Upload userpic."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(schema.album_id)

    media_repository = MediaRepository(session, cache)
    media = await media_repository.upload(current_user, album, schema.file)
    return {"media_id": media.id}


@router.get('/media/{media_id}', tags=['media'])
async def select_media(media_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       current_user=Depends(auth_reader)):
    """Select an album."""
    media_repository = MediaRepository(session, cache)
    media = await media_repository.select(media_id)
    return media.to_dict()


@router.put('/media/{media_id}', tags=['media'])
async def update_media(media_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       schema = Depends(MediaUpdateSchema), current_user=Depends(auth_editor)):
    """Update album."""
    media_repository = MediaRepository(session, cache)
    media = await media_repository.select(media_id)
    
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(schema.album_id)

    await media_repository.update(media, album, schema.media_name, media_summary=schema.media_summary)
    return {}


@router.delete('/media/{media_id}', tags=['media'])
async def delete_media(media_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       current_user=Depends(auth_admin)):
    """Delete media."""
    media_repository = MediaRepository(session, cache)
    media = await media_repository.select(media_id)

    await media_repository.delete(media)
    return {}

@router.get('/medias', tags=['media'])
async def media_list(session = Depends(get_session), cache = Depends(get_cache),
                     schema = Depends(MediaListSchema), current_user=Depends(auth_reader)):
    """Get users list."""
    media_repository = MediaRepository(session, cache)

    kwargs = {key[0]: key[1] for key in schema if key[1]}
    medias = await media_repository.select_all(**kwargs)
    medias_count = await media_repository.count_all(**kwargs)
    return {
        "medias": [media.to_dict() for media in medias],
        "medias_count": medias_count,
    }
