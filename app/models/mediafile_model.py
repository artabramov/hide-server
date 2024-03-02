"""Mediafile SQLAlchemy model."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.models.tag_model import MediafileTag


class Mediafile(Base):
    """Mediafile SQLAlchemy model."""

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
    mediafile_description = Column(String(512), index=False, nullable=True)
    comments_count = Column(Integer, index=True, nullable=False, default=0)

    mediafile_user = relationship("User", back_populates="mediafile", lazy="joined")
    mediafile_album = relationship("Album", back_populates="mediafile", lazy="joined")
    mediafile_metadata = relationship("Metadata", back_populates="mediafile", lazy="joined", cascade="all,delete")
    mediafile_colorset = relationship("Colorset", back_populates="mediafile", lazy="joined", uselist=False, cascade="all,delete")
    mediafile_tags = relationship("Tag", secondary=MediafileTag.__table__, back_populates="mediafiles", lazy="joined")

    favorite = relationship("Favorite", back_populates="favorite_mediafile", lazy="noload")
    comment = relationship("Comment", back_populates="comment_mediafile", lazy="noload")

    def __init__(self, user_id: int, album_id: int, original_filename: str, filename: str, thumbnail: str, 
                 filesize: int=None, mimetype: str=None, width: int=None, height: int=None,
                 format: str=None, mode: str=None, mediafile_description: str = None):
        """Init Mediafile model."""
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
        self.mediafile_description = mediafile_description
        self.comments_count = 0

    def to_dict(self):
        """Return Mediafile model as dictionary."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "album_id": self.album_id,
            "original_filename": self.original_filename,
            "filename": self.filename,
            "filesize": self.filesize,
            "width": self.width,
            "height": self.height,
            "mimetype": self.mimetype,
            "format": self.format,
            "mode": self.mode,
            "thumbnail": self.thumbnail,
            "mediafile_description": self.mediafile_description,
            "comments_count": self.comments_count,
            "mediafile_metadata": {x.meta_key: x.meta_value for x in self.mediafile_metadata},
            "mediafile_colorset": self.mediafile_colorset.to_dict() if self.mediafile_colorset else {},
            "mediafile_tags": [x.tag_value for x in self.mediafile_tags],
        }
