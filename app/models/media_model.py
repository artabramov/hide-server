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
    media_summary = Column(String(512), index=False, nullable=True)

    filename = Column(String(512), nullable=False, unique=True)
    mimetype = Column(String(512), nullable=False, index=True)
    filesize = Column(Integer, nullable=False, index=True)
    width = Column(Integer, nullable=False, index=True)
    height = Column(Integer, nullable=False, index=True)
    format = Column(String(40), nullable=False, index=True)
    mode = Column(String(40), nullable=False, index=True)

    # media_ext = Column(String(512), nullable=True, index=True)

    thumbnail = Column(String(512), nullable=True, unique=True)
    comments_count = Column(Integer, index=True, nullable=False, default=0)

    user = relationship("User", back_populates="media", lazy="joined")
    album = relationship("Album", back_populates="media", lazy="joined")
    exif = relationship("Exif", back_populates="media", lazy="joined", cascade="all,delete")

    def __init__(self, user_id: int, album_id: int, media_name: str, filename: str, filesize: int, width: int,
                 height: int, mimetype: str,  format: str, mode: str, thumbnail: str, media_summary: str = None):
        """Init user SQLAlchemy object."""
        self.user_id = user_id
        self.album_id = album_id
        self.media_name = media_name
        self.media_summary = media_summary
        self.filename = filename
        self.filesize = filesize
        self.width = width
        self.height = height
        self.mimetype = mimetype
        self.format = format
        self.mode = mode
        self.thumbnail = thumbnail

    def to_dict(self):
        """Return model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "media_name": self.media_name,
            # "user_id": self.user_id,
            # "album_name": self.album_name,
            # "album_summary": self.album_summary,
            # "media_count": self.media_count,
            # "media_size": self.media_size,
            # "user": self.user.to_dict(),
            "exif": {x.exif_key: x.exif_value for x in self.exif},
        }
