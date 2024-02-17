"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Album(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "albums"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    album_name = Column(String(128), nullable=False, index=True)
    album_summary = Column(String(512), index=False, nullable=True)
    media_count = Column(Integer, index=True, nullable=False, default=0)
    media_size = Column(BigInteger, index=True, nullable=False, default=0)

    user = relationship("User", back_populates="album", lazy="joined")
    media = relationship("Media", back_populates="album", lazy="noload")

    def __init__(self, user_id: int, album_name: str, album_summary: str = None):
        """Init user SQLAlchemy object."""
        self.user_id = user_id
        self.album_name = album_name
        self.album_summary = album_summary
        self.media_count = 0
        self.media_size = 0

    def to_dict(self):
        """Return model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "album_name": self.album_name,
            "album_summary": self.album_summary,
            "media_count": self.media_count,
            "media_size": self.media_size,
            "user": self.user.to_dict(),
        }
