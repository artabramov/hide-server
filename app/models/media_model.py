"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Media(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "media"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    album_id = Column(BigInteger, ForeignKey('albums.id'), index=True, nullable=False)
    media_name = Column(String(512), nullable=False, index=True)
    media_ext = Column(String(512), nullable=True, index=True)
    media_mime = Column(String(512), nullable=False, index=True)
    media_size = Column(Integer, nullable=False, index=True)
    media_width = Column(Integer, nullable=False, index=True)
    media_height = Column(Integer, nullable=False, index=True)
    media_file = Column(String(512), nullable=False, unique=True)
    media_thumbnail = Column(String(512), nullable=True, unique=True)
    comments_count = Column(Integer, index=True, nullable=False, default=0)

    user = relationship("User", back_populates="media", lazy="joined")
    album = relationship("User", back_populates="album", lazy="joined")

    def __init__(self, user_id: int, album_id: int, album_summary: str = None):
        """Init user SQLAlchemy object."""
        self.user_id = user_id
        self.album_name = album_name
        self.album_summary = album_summary
        self.mediafiles_count = 0
        self.mediafiles_size = 0

    def to_dict(self):
        """Return model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "album_name": self.album_name,
            "album_summary": self.album_summary,
            "mediafiles_count": self.mediafiles_count,
            "mediafiles_size": self.mediafiles_size,
            "user": self.user.to_dict(),
        }
