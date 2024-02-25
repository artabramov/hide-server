"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg
# from app.models.tag_model import mediafiles_tags
from app.models.tag_model import MediafileTag

cfg = get_cfg()


class Mediafile(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "mediafiles"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    album_id = Column(BigInteger, ForeignKey("albums.id"), index=True, nullable=False)

    original_filename = Column(String(512), nullable=False, index=True)
    filename = Column(String(512), nullable=False, unique=True)
    mimetype = Column(String(512), nullable=False, index=True)
    filesize = Column(BigInteger, nullable=False, index=True)
    width = Column(Integer, nullable=False, index=True)
    height = Column(Integer, nullable=False, index=True)
    format = Column(String(40), nullable=False, index=True)
    mode = Column(String(40), nullable=False, index=True)
    thumbnail = Column(String(512), nullable=True, unique=True)
    mediafile_summary = Column(String(512), index=False, nullable=True)
    comments_count = Column(Integer, index=True, nullable=False, default=0)

    user = relationship("User", back_populates="mediafile", lazy="joined")
    album = relationship("Album", back_populates="mediafile", lazy="joined")
    favorite = relationship("Favorite", back_populates="favorite_mediafile", lazy="noload")
    mediafile_metadata = relationship("Metadata", back_populates="mediafile", lazy="joined", cascade="all,delete")
    mediafile_colorset = relationship("Colorset", back_populates="mediafile", lazy="joined", uselist=False, cascade="all,delete")
    mediafile_tags = relationship("Tag", secondary=MediafileTag.__table__, back_populates="mediafiles", lazy="joined")

    def __init__(self, user_id: int, album_id: int, original_filename: str, filename: str, filesize: int, width: int,
                 height: int, mimetype: str,  format: str, mode: str, thumbnail: str, mediafile_summary: str = None):
        """Init user SQLAlchemy object."""
        self.user_id = user_id
        self.album_id = album_id
        self.original_filename = original_filename
        self.filename = filename
        self.filesize = filesize
        self.width = width
        self.height = height
        self.mimetype = mimetype
        self.format = format
        self.mode = mode
        self.thumbnail = thumbnail
        self.mediafile_summary = mediafile_summary
        self.comments_count = 0

    def to_dict(self):
        """Return model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "original_filename": self.original_filename,
            "mediafile_metadata": {x.meta_key: x.meta_value for x in self.mediafile_metadata},
            "mediafile_colorset": self.mediafile_colorset.to_dict() if self.mediafile_colorset else {},
            "mediafile_tags": [x.tag_value for x in self.mediafile_tags],
        }
