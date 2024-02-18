"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Mediafile(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "mediafiles"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    album_id = Column(BigInteger, ForeignKey('albums.id'), index=True, nullable=False)

    mediafile_name = Column(String(512), nullable=False, index=True)
    mediafile_summary = Column(String(512), index=False, nullable=True)

    filename = Column(String(512), nullable=False, unique=True)
    mimetype = Column(String(512), nullable=False, index=True)
    filesize = Column(Integer, nullable=False, index=True)
    width = Column(Integer, nullable=False, index=True)
    height = Column(Integer, nullable=False, index=True)
    format = Column(String(40), nullable=False, index=True)
    mode = Column(String(40), nullable=False, index=True)

    # mediafile_ext = Column(String(512), nullable=True, index=True)

    thumbnail = Column(String(512), nullable=True, unique=True)
    comments_count = Column(Integer, index=True, nullable=False, default=0)

    user = relationship("User", back_populates="mediafile", lazy="joined")
    album = relationship("Album", back_populates="mediafile", lazy="joined")
    attributes = relationship("Attribute", back_populates="mediafile", lazy="joined", cascade="all,delete")

    def __init__(self, user_id: int, album_id: int, mediafile_name: str, filename: str, filesize: int, width: int,
                 height: int, mimetype: str,  format: str, mode: str, thumbnail: str, mediafile_summary: str = None):
        """Init user SQLAlchemy object."""
        self.user_id = user_id
        self.album_id = album_id
        self.mediafile_name = mediafile_name
        self.mediafile_summary = mediafile_summary
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
            "mediafile_name": self.mediafile_name,
            "attributes": {x.attribute_key: x.attribute_value for x in self.attributes},
        }
