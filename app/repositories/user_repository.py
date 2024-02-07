"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.models.user_models import User
from app.helpers.jwt_helper import JWTHelper
from app.helpers.mfa_helper import MFAHelper
from app.errors import E


class UserRepository:
    """User repository."""

    def __init__(self, session, cache) -> None:
        """Init User Repository."""
        self.session = session
        self.cache = cache

    async def register(self, user_login: str, user_pass: str, first_name: str, last_name: str):
        """Register a new user."""
        entity_manager = EntityManager(self.session)
        if await entity_manager.exists(User, user_login__eq=user_login):
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "value_exists", "msg": E.VALUE_EXISTS})

        try:
            mfa_key = MFAHelper.create_mfa_key()
            MFAHelper.create_mfa_image(user_login, mfa_key)

            jti = JWTHelper.create_jti()
            user = User(user_login, user_pass, first_name, last_name, mfa_key, jti)
            await entity_manager.insert(user)

            cache_manager = CacheManager(self.cache)
            await cache_manager.set(user)

            await entity_manager.commit()

        except Exception as e:
            await MFAHelper.delete_mfa_image(mfa_key)
            await entity_manager.rollback()
            raise e

        return user
