"""User repository."""

# from app.models.user_models import User, UserMeta, UserRole
# from app.models.user_models import USER_PASS_ATTEMPTS_LIMIT, USER_PASS_SUSPENDED_TIME, USER_MFA_ATTEMPTS_LIMIT
# from app.managers.entity_manager import EntityManager
# from app.errors import E
# from app.helpers.mfa_helper import MFAHelper
# from app.helpers.jwt_helper import JWTHelper
# from app.dotenv import get_config
# from fastapi import HTTPException, UploadFile
# from app.helpers.hash_helper import HashHelper
# from fastapi.exceptions import RequestValidationError
# from app.repositories.meta_repository import MetaRepository
# from app.managers.file_manager import FileManager
# from PIL import Image
# import time

# config = get_config()
# jwt_helper = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)
# hash_helper = HashHelper(config.HASH_SALT)

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
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
            await entity_manager.insert(user, commit=True)

        except Exception as e:
            # await MFAHelper.delete_mfa_image(mfa_key)
            await entity_manager.rollback()
            raise e

        return user
