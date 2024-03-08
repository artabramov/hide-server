from fastapi import APIRouter, Depends, HTTPException
from app.session import get_session
from app.cache import get_cache
from app.schemas.album_schemas import AlbumSchema, AlbumInsertSchema, AlbumUpdateSchema, AlbumsListSchema
from app.repositories.album_repository import AlbumRepository
from app.auth import auth_editor, auth_reader
from app.models.album_model import Album

router = APIRouter()


@router.post('/album', tags=['albums'])
async def insert_album(session=Depends(get_session), cache=Depends(get_cache), schema=Depends(AlbumInsertSchema),
                       current_user=Depends(auth_editor)):
    """Insert album."""
    album_repository = AlbumRepository(session, cache)
    album = Album(current_user.id, schema.is_locked, schema.album_name, album_description=schema.album_description)
    album = await album_repository.insert(album, commit=True)
    return {
        "album_id": album.id,
    }


@router.get('/album/{album_id}', tags=['albums'], response_model=AlbumSchema)
async def select_album(album_id: int, session=Depends(get_session), cache=Depends(get_cache),
                       current_user=Depends(auth_reader)):
    """Select album."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id)
    if not album:
        raise HTTPException(status_code=404)

    return album.to_dict()


@router.put('/album/{album_id}', tags=['albums'])
async def update_album(album_id: int, session=Depends(get_session), cache=Depends(get_cache),
                       schema=Depends(AlbumUpdateSchema), current_user=Depends(auth_editor)):
    """Update album."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id)
    if not album:
        raise HTTPException(status_code=404)

    album.is_locked = schema.is_locked
    album.album_name = schema.album_name
    album.album_description = schema.album_description
    await album_repository.update(album, commit=True)
    return {}


@router.delete('/delete/{album_id}', tags=['albums'])
async def delete_album(album_id: int, session=Depends(get_session), cache=Depends(get_cache),
                       current_user=Depends(auth_editor)):
    """Delete album."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id)
    if not album:
        raise HTTPException(status_code=404)

    # TODO: delete mediafiles, etc
    if album.mediafiles_count > 0:
        pass

    await album_repository.delete(album, commit=True)
    return {}


@router.get('/albums', tags=['albums'])
async def albums_list(session = Depends(get_session), cache = Depends(get_cache),
                      schema = Depends(AlbumsListSchema), current_user=Depends(auth_reader)):
    """Albums list."""
    album_repository = AlbumRepository(session, cache)
    albums = await album_repository.select_all(**schema.kwargs)
    users_count = await album_repository.count_all(**schema.kwargs)
    return {
        "albums": [album.to_dict() for album in albums],
        "albums_count": users_count,
    }
