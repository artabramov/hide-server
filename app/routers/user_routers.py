from fastapi import APIRouter, Depends
from app.session import get_session
from app.cache import get_cache
from app.schemas.user_schemas import UserRegisterRequest, UserLoginRequest, TokenSelectRequest
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.post('/user', tags=['users'])
async def user_register(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserRegisterRequest)):
    user_repository = UserRepository(session, cache)
    user = await user_repository.register(schema.user_login, schema.user_pass, schema.first_name, schema.last_name)
    return {
        "user_id": user.id,
        "mfa_key": user.mfa_key,
        'mfa_image': user.mfa_image,
    }


@router.get('/auth/login', tags=['auth'])
async def user_login(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserLoginRequest)):
    """User login."""
    user_repository = UserRepository(session, cache)
    await user_repository.login(schema.user_login, schema.user_pass.get_secret_value())
    return {
        "pass_accepted": True,
    }


@router.get('/auth/token', tags=['auth'])
async def token_select(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(TokenSelectRequest)):
    """Get JWT token."""
    user_repository = UserRepository(session, cache)
    user_token = await user_repository.token_select(schema.user_login, schema.user_totp, schema.exp)
    return {
        "user_token": user_token,
    }
