from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.album_schemas import AlbumEditSchema, AlbumSchema
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


# @router.put('/user/pass', tags=['users'])
# async def update_password(session = Depends(get_session), cache = Depends(get_cache),
#                       schema = Depends(PassUpdateSchema), current_user=Depends(auth_reader)):
#     """Update user password."""
#     user_repository = UserRepository(session, cache)
#     await user_repository.pass_update(current_user, schema.user_pass.get_secret_value(),
#                                       schema.user_pass_new.get_secret_value())
#     return {}


# @router.put('/user/{user_id}/role', tags=['users'])
# async def update_role(user_id: int, session = Depends(get_session), cache = Depends(get_cache),
#                       current_user=Depends(auth_admin), schema = Depends(RoleUpdateSchema)):
#     """Update user role."""
#     if current_user.id == user_id:
#         raise RequestValidationError({"loc": ["path", "user_id"], "input": user_id,
#                                      "type": "value_locked", "msg": E.VALUE_LOCKED})

#     user_repository = UserRepository(session, cache)
#     user = await user_repository.select(user_id)
    
#     await user_repository.role_update(user, schema.user_role)
#     return {}


# @router.delete('/user/{user_id}', tags=['users'])
# async def delete_user(user_id: int, session = Depends(get_session), cache = Depends(get_cache),
#                       current_user=Depends(auth_admin)):
#     """Delete user."""
#     if current_user.id == user_id:
#         raise RequestValidationError({"loc": ["path", "user_id"], "input": user_id,
#                                      "type": "value_locked", "msg": E.VALUE_LOCKED})

#     user_repository = UserRepository(session, cache)
#     user = await user_repository.select(user_id)
#     await user_repository.delete(user)
#     return {}


# @router.get('/users', tags=['users'])
# async def users_list(session = Depends(get_session), cache = Depends(get_cache),
#                      schema = Depends(UsersListSchema), current_user=Depends(auth_reader)):
#     """Get users list."""
#     user_repository = UserRepository(session, cache)

#     kwargs = {key[0]: key[1] for key in schema if key[1]}
#     users = await user_repository.select_all(**kwargs)
#     users_count = await user_repository.count_all(**kwargs)
#     return {
#         "users": [user.to_dict() for user in users],
#         "users_count": users_count,
#     }


# @router.post('/user/userpic', tags=['users'])
# async def upload_userpic(session = Depends(get_session), cache = Depends(get_cache),
#                          schema = Depends(UserpicUploadSchema), current_user=Depends(auth_reader)):
#     """Upload userpic."""
#     user_repository = UserRepository(session, cache)
#     await user_repository.userpic_upload(current_user, schema.file)
#     return {}


# @router.delete('/user/userpic', tags=['users'])
# async def userpic_delete(session = Depends(get_session), cache = Depends(get_cache), current_user=Depends(auth_reader)):
#     """Delete userpic."""
#     user_repository = await UserRepository(session, cache)
#     await user_repository.userpic_delete(current_user)
#     return {}
