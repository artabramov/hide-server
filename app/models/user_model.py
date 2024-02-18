"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Boolean, Column, Integer, BigInteger, SmallInteger, String, Enum
from app.session import Base
from sqlalchemy.ext.hybrid import hybrid_property
from app.helpers.hash_helper import HashHelper
from app.mixins.fernet_mixin import FernetMixin
from sqlalchemy.orm import relationship
from app.config import get_cfg

cfg = get_cfg()


class UserRole(enum.Enum):
    """SQLAlchemy model for user role."""

    denied = "denied"
    reader = "reader"
    writer = "writer"
    editor = "editor"
    admin = "admin"


class User(Base, FernetMixin):
    """SQLAlchemy model for user."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    suspended_date = Column(Integer, nullable=False, default=0)
    user_role = Column(Enum(UserRole), nullable=False, index=True, default=UserRole.denied)
    user_login = Column(String(40), nullable=False, index=True, unique=True)
    first_name = Column(String(40), nullable=False, index=True)
    last_name = Column(String(40), nullable=False, index=True)
    pass_hash = Column(String(128), nullable=False, index=True)
    pass_attempts = Column(SmallInteger, nullable=False, default=0)
    pass_accepted = Column(Boolean, nullable=False, default=False)
    mfa_key_encrypted = Column(String(512), nullable=False, unique=True)
    mfa_attempts = Column(SmallInteger(), nullable=False, default=0)
    jti_encrypted = Column(String(512), nullable=False, unique=True)
    userpic = Column(String(128), index=False, unique=True, nullable=True)
    user_summary = Column(String(512), index=False, nullable=True)

    album = relationship("Album", back_populates="user", lazy="noload")
    mediafile = relationship("Mediafile", back_populates="user", lazy="noload")

    def __init__(self, user_login: str, user_pass: str, first_name: str, last_name: str, mfa_key: str, jti: str):
        """Init user SQLAlchemy object."""
        self.suspended_date = 0
        self.user_role = UserRole.denied
        self.user_login = user_login
        self.user_pass = user_pass
        self.first_name = first_name
        self.last_name = last_name
        self.pass_attempts = 0
        self.pass_accepted = False
        self.mfa_key = mfa_key
        self.mfa_attempts = 0
        self.jti = jti

    def __setattr__(self, key: str, value):
        """Set pass hash."""
        if key == 'user_pass':
            self.pass_hash = HashHelper.get_hash(value)
        else:
            super().__setattr__(key, value)

    @property
    def mfa_key(self):
        return self.decrypt_value(self.mfa_key_encrypted)

    @mfa_key.setter
    def mfa_key(self, value: str):
        self.mfa_key_encrypted = self.encrypt_value(value)

    @property
    def mfa_image(self):
        return cfg.MFA_URL + self.mfa_key + cfg.MFA_EXTENSION

    @property
    def jti(self):
        return self.decrypt_value(self.jti_encrypted)

    @jti.setter
    def jti(self, value: str):
        self.jti_encrypted = self.encrypt_value(value)

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

    def to_dict(self) -> dict:
        """Return model as dict."""
        return {
            'id': self.id,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'user_role': self.user_role.name,
            'user_login': self.user_login,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'userpic': cfg.USERPIC_URL + self.userpic if self.userpic else None,
            'user_summary': self.user_summary,
        }