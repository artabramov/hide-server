from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.user_schemas import UserSchema, UserRegisterSchema, UserLoginSchema, TokenSelectSchema, UserUpdateSchema, PassUpdateSchema, RoleUpdateSchema, UsersListSchema
from app.repositories.user_repository import UserRepository
from app.auth import auth_admin, auth_reader
from app.errors import E

router = APIRouter()


@router.get('/auth/login', tags=['auth'])
async def login(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserLoginSchema)):
    """User login."""
    user_repository = UserRepository(session, cache)
    await user_repository.login(schema.user_login, schema.user_pass.get_secret_value())
    return {
        "pass_accepted": True,
    }


@router.get('/auth/token', tags=['auth'])
async def get_token(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(TokenSelectSchema)):
    """Get JWT token."""
    user_repository = UserRepository(session, cache)
    user_token = await user_repository.token_select(schema.user_login, schema.user_totp, schema.exp)
    return {
        "user_token": user_token,
    }


@router.delete('/auth/token', tags=['auth'])
async def delete_token(session = Depends(get_session), cache = Depends(get_cache), current_user=Depends(auth_reader)):
    """Delete JWT token."""
    user_repository = UserRepository(session, cache)
    await user_repository.token_delete(current_user)
    return {}


@router.post('/user', tags=['users'])
async def register_user(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserRegisterSchema)):
    user_repository = UserRepository(session, cache)
    user = await user_repository.register(schema.user_login, schema.user_pass.get_secret_value(), schema.first_name,
                                          schema.last_name)
    return {
        "user_id": user.id,
        "mfa_key": user.mfa_key,
        'mfa_image': user.mfa_image,
    }


@router.get('/user/{user_id}', tags=['users'], response_model=UserSchema)
async def select_user(user_id: int, session = Depends(get_session), cache = Depends(get_cache),
                      current_user=Depends(auth_reader)):
    """Select a user."""
    user_repository = UserRepository(session, cache)
    user = await user_repository.select(user_id)
    return user.to_dict()


@router.put('/user', tags=['users'])
async def update_user(session = Depends(get_session), cache = Depends(get_cache),
                      schema = Depends(UserUpdateSchema), current_user=Depends(auth_reader)):
    """Update current user."""
    user_repository = UserRepository(session, cache)
    await user_repository.update(current_user, schema.first_name, schema.last_name, user_summary=schema.user_summary)
    return {}


@router.put('/user/pass', tags=['users'])
async def update_password(session = Depends(get_session), cache = Depends(get_cache),
                      schema = Depends(PassUpdateSchema), current_user=Depends(auth_reader)):
    """Update user password."""
    user_repository = UserRepository(session, cache)
    await user_repository.pass_update(current_user, schema.user_pass.get_secret_value(),
                                      schema.user_pass_new.get_secret_value())
    return {}


@router.put('/user/{user_id}/role', tags=['users'])
async def update_role(user_id: int, session = Depends(get_session), cache = Depends(get_cache),
                      current_user=Depends(auth_admin), schema = Depends(RoleUpdateSchema)):
    """Update user role."""
    if current_user.id == user_id:
        raise RequestValidationError({"loc": ["path", "user_id"], "input": user_id,
                                     "type": "value_locked", "msg": E.VALUE_LOCKED})

    user_repository = UserRepository(session, cache)
    user = await user_repository.select(user_id)
    
    await user_repository.role_update(user, schema.user_role)
    return {}


@router.delete('/user/{user_id}', tags=['users'])
async def delete_user(user_id: int, session = Depends(get_session), cache = Depends(get_cache),
                      current_user=Depends(auth_admin)):
    """Delete user."""
    if current_user.id == user_id:
        raise RequestValidationError({"loc": ["path", "user_id"], "input": user_id,
                                     "type": "value_locked", "msg": E.VALUE_LOCKED})

    user_repository = UserRepository(session, cache)
    user = await user_repository.select(user_id)
    await user_repository.delete(user)
    return {}


@router.get('/users', tags=['users'])
async def users_list(session = Depends(get_session), cache = Depends(get_cache),
                     schema = Depends(UsersListSchema), current_user=Depends(auth_reader)):
    """Get users list."""
    user_repository = UserRepository(session, cache)

    kwargs = {key[0]: key[1] for key in schema if key[1]}
    users = await user_repository.select_all(**kwargs)
    users_count = await user_repository.count_all(**kwargs)
    return {
        "users": [user.to_dict() for user in users],
        "users_count": users_count,
    }
