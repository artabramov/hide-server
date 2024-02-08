"""Authentication."""

from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.errors import E
from app.helpers.jwt_helper import JWTHelper
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.config import get_cfg
from app.session import get_session
from app.cache import get_cache
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.models.user_models import User
from fastapi import HTTPException

JWT_ERROR_LOC = ("header", "Authorization")

cfg = get_cfg()
jwt_schema = HTTPBearer()


async def _auth_user(user_token):
    if not user_token.credentials:
        raise HTTPException(status_code=403, detail=E.JWT_EMPTY)

    try:
        jwt_payload = JWTHelper.decode_token(user_token.credentials)

    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail=E.JWT_EXPIRED)

    except PyJWTError:
        raise HTTPException(status_code=403, detail=E.JWT_INVALID)

    cache = await anext(get_cache())
    cache_manager = CacheManager(cache)
    user = await cache_manager.get(User, jwt_payload["user_id"])

    if not user:
        session = await anext(get_session())
        entity_manager = EntityManager(session)
        user = await entity_manager.select_by(User, id__eq=jwt_payload["user_id"])

    if not user:
        raise HTTPException(status_code=403, detail=E.jwt_rejected)

    await cache_manager.set(user)

    if jwt_payload["jti"] != user.jti:
        raise HTTPException(status_code=403, detail=E.jwt_rejected)

    return user


async def auth_admin(user_token: Annotated[str, Depends(jwt_schema)]):
    """Authenticate admin user."""
    user = await _auth_user(user_token)
    if not user.can_admin:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user


async def auth_editor(user_token: Annotated[str, Depends(jwt_schema)]):
    """Authenticate editor user."""
    user = await _auth_user(user_token)
    if not user.can_edit:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user


async def auth_writer(user_token: Annotated[str, Depends(jwt_schema)]):
    """Authenticate writer user."""
    user = await _auth_user(user_token)
    if not user.can_write:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user


async def auth_reader(user_token: Annotated[str, Depends(jwt_schema)]):
    """Authenticate reader user."""
    user = await _auth_user(user_token)
    if not user.can_read:
        raise HTTPException(status_code=403, detail=E.jwt_denied)

    return user
