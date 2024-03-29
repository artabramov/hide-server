"""User repository."""

from fastapi.exceptions import RequestValidationError
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
from app.models.user_model import User, UserRole
from app.helpers.jwt_helper import JWTHelper
from app.helpers.mfa_helper import MFAHelper
from app.helpers.hash_helper import HashHelper
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps
from app.errors import E
from app.config import get_cfg
import time
import os

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
            await entity_manager.commit()

            cache_manager = CacheManager(self.cache)
            await cache_manager.set(user)

        except Exception as e:
            await MFAHelper.delete_mfa_image(mfa_key)
            await entity_manager.rollback()
            raise e

        return user

    async def login(self, user_login: str, user_pass: str):
        """User login."""
        entity_manager = EntityManager(self.session)
        user = await entity_manager.select_by(User, user_login__eq=user_login)
        admin_exists = await entity_manager.exists(User, user_role__eq=UserRole.admin)

        if not user:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "value_invalid", "msg": E.LOGIN_INVALID})

        elif user.user_role.name == UserRole.denied.name and admin_exists:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.USER_LOGIN_DENIED})

        elif user.suspended_date >= time.time():
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_suspended", "msg": E.USER_LOGIN_SUSPENDED})

        elif user.pass_hash == HashHelper.get_hash(user_pass):
            user.suspended_date = 0
            user.pass_attempts = 0
            user.pass_accepted = True
            await entity_manager.update(user, commit=True)
            
            cache_manager = CacheManager(self.cache)
            await cache_manager.set(user)

        else:
            user.suspended_date = 0
            user.pass_attempts = user.pass_attempts + 1
            user.pass_accepted = False
            if user.pass_attempts >= cfg.USER_PASS_ATTEMPTS_LIMIT:
                user.suspended_date = int(time.time()) + cfg.USER_LOGIN_SUSPENDED_TIME
                user.pass_attempts = 0

            await entity_manager.update(user, commit=True)

            cache_manager = CacheManager(self.cache)
            await cache_manager.set(user)

            raise RequestValidationError({"loc": ["query", "user_pass"], "input": user_pass,
                                          "type": "pass_invalid", "msg": E.USER_PASS_INVALID})


    async def token_select(self, user_login: str, user_totp: str, exp: int = None) -> str:
        """Get user token."""
        entity_manager = EntityManager(self.session)
        user = await entity_manager.select_by(User, user_login__eq=user_login)
        admin_exists = await entity_manager.exists(User, user_role__eq=UserRole.admin)

        if not user:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_invalid", "msg": E.USER_LOGIN_INVALID})

        elif user.user_role.name == UserRole.denied.name and admin_exists:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.USER_LOGIN_DENIED})

        elif not user.pass_accepted:
            raise RequestValidationError({"loc": ["query", "user_login"], "input": user_login,
                                          "type": "login_denied", "msg": E.USER_LOGIN_DENIED})

        if user_totp == MFAHelper.get_mfa_totp(user.mfa_key):

            await MFAHelper.delete_mfa_image(user.mfa_key)
            user.mfa_attempts = 0
            user.pass_accepted = False
            if not admin_exists:
                user.user_role = UserRole.admin
            await entity_manager.update(user, commit=True)

            cache_manager = CacheManager(self.cache)
            await cache_manager.set(user)

            user_token = JWTHelper.encode_token(user.id, user.user_role.name, user.user_login, user.jti, exp)
            return user_token

        else:
            user.mfa_attempts = user.mfa_attempts + 1
            if user.mfa_attempts >= cfg.USER_MFA_ATTEMPTS_LIMIT:
                user.mfa_attempts = 0
                user.pass_accepted = False

            await entity_manager.update(user, commit=True)

            cache_manager = CacheManager(self.cache)
            await cache_manager.set(user)

            raise RequestValidationError({"loc": ["query", "user_totp"], "input": user_totp,
                                          "type": "value_invalid", "msg": E.USER_TOTP_INVALID})


    async def select(self, user_id: int):
        """Select user."""
        cache_manager = CacheManager(self.cache)
        user = await cache_manager.get(User, user_id)

        if not user:
            entity_manager = EntityManager(self.session)
            user = await entity_manager.select(User, user_id)

        if not user:
            raise HTTPException(status_code=404)

        await cache_manager.set(user)
        return user

    async def update(self, user: User, first_name: str, last_name: str, user_summary: str = None):
        """Update user."""
        user.first_name = first_name
        user.last_name = last_name
        user.user_summary = user_summary
        
        entity_manager = EntityManager(self.session)
        await entity_manager.update(user, commit=True)

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(user)

    async def pass_update(self, user: User, user_pass: str, user_pass_new: str):
        """Update user password."""
        if user.pass_hash != HashHelper.get_hash(user_pass):
            raise RequestValidationError({"loc": ["query", "user_pass"], "input": user_pass,
                                          "type": "pass_invalid", "msg": E.USER_PASS_INVALID})

        user.user_pass = user_pass_new

        entity_manager = EntityManager(self.session)
        await entity_manager.update(user, commit=True)

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(user)


    async def role_update(self, user: User, user_role: str):
        """Update user role."""
        user.user_role = user_role

        entity_manager = EntityManager(self.session)
        await entity_manager.update(user, commit=True)

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(user)


    async def delete(self, user: User):
        """Delete user."""
        entity_manager = EntityManager(self.session)
        try:
            await entity_manager.delete(user, commit=True)
        except Exception:
            raise RequestValidationError({"loc": ["path", "user_id"], "input": user.id,
                                         "type": "value_locked", "msg": E.VALUE_LOCKED})

        cache_manager = CacheManager(self.cache)
        await cache_manager.delete(user)

    async def select_all(self, **kwargs):
        """Select all users."""
        entity_manager = EntityManager(self.session)
        users = await entity_manager.select_all(User, **kwargs)

        cache_manager = CacheManager(self.cache)
        for user in users:
            await cache_manager.set(user)
        return users

    async def count_all(self, **kwargs):
        """Count users."""
        entity_manager = EntityManager(self.session)
        users_count = await entity_manager.count_all(User, **kwargs)
        return users_count


    async def userpic_upload(self, user: User, file: UploadFile):
        """Upload userpic."""
        if file.content_type not in cfg.USERPIC_MIMES:
            raise RequestValidationError({"loc": ["file", "file"], "input": file.content_type,
                                          "type": "file_mime", "msg": E.FILE_MIME_INVALID})

        userpic = await FileManager.file_upload(file, cfg.USERPIC_PATH)
        userpic_path = os.path.join(cfg.USERPIC_PATH, userpic)

        original_image = Image.open(userpic_path)
        userpic_image = ImageOps.fit(original_image, tuple([cfg.USERPIC_WIDTH, cfg.USERPIC_HEIGHT]), Image.LANCZOS)
        userpic_image.save(userpic_path, image_quality=cfg.USERPIC_QUALITY)

        await self.userpic_delete(user)
        user.userpic = userpic

        entity_manager = EntityManager(self.session)
        await entity_manager.update(user, commit=True)

        cache_manager = CacheManager(self.cache)
        await cache_manager.set(user)

    async def userpic_delete(self, user: User):
        """Delete userpic."""
        if user.userpic:
            userpic_path = os.path.join(cfg.USERPIC_PATH, user.userpic)
            await FileManager.file_delete(userpic_path)

            user.userpic = None

            entity_manager = EntityManager(self.session)
            await entity_manager.update(user, commit=True)

            cache_manager = CacheManager(self.cache)
            await cache_manager.set(user)
