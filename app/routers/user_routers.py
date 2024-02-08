from fastapi import APIRouter, Depends
from app.session import get_session
from app.cache import get_cache
from app.schemas.user_schemas import UserSchema, UserSelectSchema, UserRegisterSchema, UserLoginSchema, TokenSelectSchema
from app.repositories.user_repository import UserRepository
from app.auth import auth_reader

router = APIRouter()


@router.post('/user', tags=['users'])
async def user_register(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserRegisterSchema)):
    user_repository = UserRepository(session, cache)
    user = await user_repository.register(schema.user_login, schema.user_pass, schema.first_name, schema.last_name)
    return {
        "user_id": user.id,
        "mfa_key": user.mfa_key,
        'mfa_image': user.mfa_image,
    }


@router.get('/user/{id}', tags=['users'], response_model=UserSchema)
async def user_select(session = Depends(get_session), cache = Depends(get_cache),
                      schema = Depends(UserSelectSchema), current_user=Depends(auth_reader)):
    """Select a user."""
    user_repository = UserRepository(session, cache)
    user = await user_repository.select(schema.id)
    return user.to_dict()


@router.get('/auth/login', tags=['auth'])
async def user_login(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserLoginSchema)):
    """User login."""
    user_repository = UserRepository(session, cache)
    await user_repository.login(schema.user_login, schema.user_pass.get_secret_value())
    return {
        "pass_accepted": True,
    }


@router.get('/auth/token', tags=['auth'])
async def token_select(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(TokenSelectSchema)):
    """Get JWT token."""
    user_repository = UserRepository(session, cache)
    user_token = await user_repository.token_select(schema.user_login, schema.user_totp, schema.exp)
    return {
        "user_token": user_token,
    }


@router.delete('/auth/token', tags=['auth'])
async def token_delete(session = Depends(get_session), cache = Depends(get_cache), current_user=Depends(auth_reader)):
    """Delete JWT token."""
    user_repository = UserRepository(session, cache)
    await user_repository.token_delete(current_user)
    return {}
