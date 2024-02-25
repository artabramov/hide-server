"""The Comment SQLAlchemy model."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Comment(Base):
    """The Comment SQLAlchemy model."""

    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    mediafile_id = Column(BigInteger, ForeignKey('mediafiles.id'), index=True, nullable=False)
    comment_content = Column(Text, nullable=False)

    comment_user = relationship("User", back_populates="comment", lazy="joined")
    comment_mediafile = relationship("Mediafile", back_populates="comment", lazy="noload")

    def __init__(self, user_id: int, mediafile_id: int, comment_content: str):
        """Init user SQLAlchemy object."""
        self.user_id = user_id
        self.mediafile_id = mediafile_id
        self.comment_content = comment_content
