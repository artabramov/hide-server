"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Metadata(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "mediafiles_metadata"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    mediafile_id = Column(BigInteger, ForeignKey('mediafiles.id'), index=True, nullable=False)
    meta_key = Column(String(128), nullable=False, index=True)
    meta_value = Column(String(512), nullable=True, index=False)

    mediafile = relationship("Mediafile", back_populates="mediafile_metadata", lazy="noload")

    def __init__(self, mediafile_id: int, meta_key: str, meta_value: str):
        """Init user SQLAlchemy object."""
        self.mediafile_id = mediafile_id
        self.meta_key = meta_key
        self.meta_value = meta_value
