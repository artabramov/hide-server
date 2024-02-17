"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Exif(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "media_exif"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    media_id = Column(BigInteger, ForeignKey('media.id'), index=True, nullable=False)
    exif_key = Column(String(128), nullable=False, index=True)
    exif_value = Column(String(512), nullable=True, index=False)

    media = relationship("Media", back_populates="exif")

    def __init__(self, media_id: int, exif_key: str, exif_value: str):
        """Init user SQLAlchemy object."""
        self.media_id = media_id
        self.exif_key = exif_key
        self.exif_value = exif_value

    # def to_dict(self):
    #     """Return model as dict."""
    #     return {
    #         "id": self.id,
    #         "created_date": self.created_date,
    #         "updated_date": self.updated_date,
    #         "media_name": self.media_name,
    #         # "user_id": self.user_id,
    #         # "album_name": self.album_name,
    #         # "album_summary": self.album_summary,
    #         # "medias_count": self.media_count,
    #         # "media_size": self.media_size,
    #         # "user": self.user.to_dict(),
    #     }
