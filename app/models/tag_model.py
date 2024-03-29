"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class MediafileTag(Base):
    __tablename__ = "mediafiles_tags"

    id = Column("id", BigInteger, primary_key=True, index=True)
    created_date = Column("created_date", Integer, nullable=False, index=True, default=lambda: int(time()))
    mediafile_id = Column("mediafile_id", BigInteger, ForeignKey("mediafiles.id"), index=True)
    tag_id = Column("tag_id", BigInteger, ForeignKey("tags.id"), index=True)

    def __init__(self, mediafile_id: int, tag_id: int):
        """Init user SQLAlchemy object."""
        self.mediafile_id = mediafile_id
        self.tag_id = tag_id


class Tag(Base):
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    tag_value = Column(String(512), nullable=False, unique=True)

    mediafiles = relationship("Mediafile", secondary=MediafileTag.__table__, back_populates="mediafile_tags", lazy="noload")

    def __init__(self, tag_value: str):
        """Init user SQLAlchemy object."""
        self.tag_value = tag_value
