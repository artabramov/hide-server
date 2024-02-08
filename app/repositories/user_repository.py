"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.models.user_models import User, UserRole
from app.helpers.jwt_helper import JWTHelper
from app.helpers.mfa_helper import MFAHelper
from app.helpers.hash_helper import HashHelper
from app.errors import E
from app.config import get_cfg
import time

cfg = get_cfg()


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

            # cache_manager = CacheManager(self.cache)
            # await cache_manager.set(user)

            await entity_manager.commit()

        except Exception as e:
            await MFAHelper.delete_mfa_image(mfa_key)
            await entity_manager.rollback()
            raise e

        return user

    async def login(self, user_login: str, user_pass: str):
        """User login."""
        entity_manager = EntityManager(self.session)
        user = await entity_manager.select_by(User, user_login__eq=user_login)

        if not user:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "value_invalid", "msg": E.LOGIN_INVALID})

        elif user.user_role.name == UserRole.none.name:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.LOGIN_DENIED})

        elif user.suspended_date >= time.time():
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_suspended", "msg": E.LOGIN_SUSPENDED})

        elif user.pass_hash == HashHelper.get_hash(user_pass):
            user.suspended_date = 0
            user.pass_attempts = 0
            user.pass_accepted = True
            await entity_manager.update(user, commit=True)
            # await self.cache_manager.delete(user)

        else:
            user.suspended_date = 0
            user.pass_attempts = user.pass_attempts + 1
            user.pass_accepted = False
            if user.pass_attempts >= cfg.USER_PASS_ATTEMPTS_LIMIT:
                user.suspended_date = int(time.time()) + cfg.USER_LOGIN_SUSPENDED_TIME
                user.pass_attempts = 0

            await entity_manager.update(user, commit=True)
            # await self.cache_manager.delete(user)

            raise RequestValidationError({"loc": ["query", "user_pass"], "input": user_pass,
                                          "type": "value_invalid", "msg": E.LOGIN_INVALID})
