"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Boolean, Column, ForeignKey, Integer, BigInteger, SmallInteger, String, Enum
from sqlalchemy.orm import relationship
# from app.conn import Base
from app.session import Base
# from app.mixins.meta_mixin import MetaMixin
from sqlalchemy.ext.hybrid import hybrid_property
# from app.helpers.fernet_helper import FernetHelper
# from app.helpers.hash_helper import HashHelper
# from config import get_config
from app.mixins.hash_mixin import HashMixin
from app.config import get_cfg

cfg = get_cfg()

USER_PASS_ATTEMPTS_LIMIT = 10
USER_PASS_SUSPENDED_TIME = 30
USER_MFA_ATTEMPTS_LIMIT = 10

# config = get_config()
# fernet_helper = FernetHelper(config.FERNET_ENCRYPTION_KEY)
# hash_helper = HashHelper(config.HASH_SALT)


class UserMeta(Base):
    """SQLAlchemy model for user meta."""

    __tablename__ = "users_meta"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    parent_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    meta_key = Column(String(40), nullable=False, index=True)
    meta_value = Column(String(512), nullable=False)

    user = relationship("User", back_populates="user_meta")

    def __init__(self, parent_id: int, meta_key: str, meta_value: str) -> None:
        """Init user  meta model."""
        self.parent_id = parent_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class UserRole(enum.Enum):
    """SQLAlchemy model for user role."""

    none = "none"
    reader = "reader"
    writer = "writer"
    editor = "editor"
    admin = "admin"


class User(Base, HashMixin):
    """SQLAlchemy model for user."""

    __tablename__ = "users"
    _encrypted_attrs = ["mfa_key", "jti"]

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    suspended_date = Column(Integer, nullable=False, default=0)
    user_role = Column(Enum(UserRole), nullable=False, index=True, default=UserRole.none)
    user_login = Column(String(40), nullable=False, index=True, unique=True)
    first_name = Column(String(40), nullable=False, index=True)
    last_name = Column(String(40), nullable=False, index=True)
    pass_hash = Column(String(128), nullable=False, index=True)
    pass_attempts = Column(SmallInteger, nullable=False, default=0)
    pass_accepted = Column(Boolean, nullable=False, default=False)
    mfa_key_encrypted = Column(String(512), nullable=False, unique=True)
    mfa_attempts = Column(SmallInteger(), nullable=False, default=0)
    jti_encrypted = Column(String(512), nullable=False, unique=True)

    user_meta = relationship("UserMeta", back_populates="user", lazy="joined", cascade="all,delete")

    def __init__(self, user_login: str, user_pass: str, first_name: str, last_name: str):
        """Init user SQLAlchemy object."""
        self.suspended_date = 0
        self.user_role = UserRole.none
        self.user_login = user_login
        self.pass_hash = self.get_hash(user_pass.get_secret_value(), cfg.APP_HASH_SALT)
        self.first_name = first_name
        self.last_name = last_name
        self.pass_attempts = 0
        self.pass_accepted = False
        self.mfa_attempts = 0

    # async def encrypt_attr(self, key: str, value: str) -> None:
    #     """Set encrypted attribute."""
    #     if key in self._encrypted_attrs:
    #         setattr(self, key + "_encrypted", await fernet_helper.encrypt_value(value))

    # async def decrypt_attr(self, key: str):
    #     """Get decrypted attribute."""
    #     if key in self._encrypted_attrs:
    #         return await fernet_helper.decrypt_value(getattr(self, key + "_encrypted"))

    @hybrid_property
    def full_name(self) -> str:
        """User full name."""
        return self.first_name + " " + self.last_name

    @property
    def can_admin(self) -> bool:
        """Does the user have admin permissions."""
        return self.user_role == UserRole.admin

    @property
    def can_edit(self) -> bool:
        """Does the user have editor permissions."""
        return self.user_role in [UserRole.admin, UserRole.editor]

    @property
    def can_write(self) -> bool:
        """Does the user have writer permissions."""
        return self.user_role in [UserRole.admin, UserRole.editor, UserRole.writer]

    @property
    def can_read(self) -> bool:
        """Does the user have reader permissions."""
        return self.user_role in [UserRole.admin, UserRole.editor, UserRole.writer, UserRole.reader]

    # @property
    # def meta(self) -> dict:
    #     """User meta values."""
    #     userpic = self.getmeta("userpic")
    #     return {
    #         "user_summary": self.getmeta("user_summary"),
    #         "user_contacts": self.getmeta("user_contacts"),
    #         "userpic": config.BASE_URL + config.USERPIC_DIR + userpic if userpic else None,
    #     }
