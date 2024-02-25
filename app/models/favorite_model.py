"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Favorite(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "favorites"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    mediafile_id = Column(BigInteger, ForeignKey('mediafiles.id'), index=True, nullable=False)

    favorite_user = relationship("User", back_populates="favorite", lazy="joined")
    favorite_mediafile = relationship("Mediafile", back_populates="favorite", lazy="noload")

    def __init__(self, user_id: int, mediafile_id: int):
        """Init user SQLAlchemy object."""
        self.user_id = user_id
        self.mediafile_id = mediafile_id
