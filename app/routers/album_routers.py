from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.album_schemas import AlbumEditSchema, AlbumSchema, AlbumsListSchema
from app.repositories.album_repository import AlbumRepository
from app.auth import auth_admin, auth_editor, auth_writer, auth_reader
from app.errors import E

router = APIRouter()


@router.post('/album', tags=['albums'])
async def insert_album(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(AlbumEditSchema),
                       current_user=Depends(auth_writer)):
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.insert(current_user.id, schema.album_name, album_summary=schema.album_summary)
    return {
        "album_id": album.id,
    }


@router.get('/album/{album_id}', tags=['albums'], response_model=AlbumSchema)
async def select_album(album_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       current_user=Depends(auth_reader)):
    """Select an album."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id)
    return album.to_dict()


@router.put('/album/{album_id}', tags=['albums'])
async def update_album(album_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       schema = Depends(AlbumEditSchema), current_user=Depends(auth_editor)):
    """Update album."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id)
    await album_repository.update(album, schema.album_name, album_summary=schema.album_summary)
    return {}


@router.delete('/delete/{album_id}', tags=['albums'])
async def delete_album(album_id: int, session = Depends(get_session), cache = Depends(get_cache),
                       current_user=Depends(auth_admin)):
    """Delete album."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id)

    if album.media_count > 0:
        raise RequestValidationError({"loc": ["path", "album_id"], "input": album_id,
                                     "type": "value_locked", "msg": E.VALUE_LOCKED})

    await album_repository.delete(album)
    return {}


@router.get('/albums', tags=['albums'])
async def users_list(session = Depends(get_session), cache = Depends(get_cache),
                     schema = Depends(AlbumsListSchema), current_user=Depends(auth_reader)):
    """Get users list."""
    album_repository = AlbumRepository(session, cache)

    kwargs = {key[0]: key[1] for key in schema if key[1]}
    albums = await album_repository.select_all(**kwargs)
    users_count = await album_repository.count_all(**kwargs)
    return {
        "albums": [album.to_dict() for album in albums],
        "albums_count": users_count,
    }
