"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Attribute(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "attributes"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    mediafile_id = Column(BigInteger, ForeignKey('mediafiles.id'), index=True, nullable=False)
    attribute_key = Column(String(128), nullable=False, index=True)
    attribute_value = Column(String(512), nullable=True, index=False)

    mediafile = relationship("Mediafile", back_populates="attributes", lazy="noload")

    def __init__(self, mediafile_id: int, attribute_key: str, attribute_value: str):
        """Init user SQLAlchemy object."""
        self.mediafile_id = mediafile_id
        self.attribute_key = attribute_key
        self.attribute_value = attribute_value
