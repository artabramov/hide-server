"""SQLAlchemy bookmark model."""

from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.models.primary_model import Primary


class Bookmark(Primary):
    """SQLAlchemy bookmark model."""

    __tablename__ = "bookmarks"

    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    mediafile_id = Column(BigInteger, ForeignKey("mediafiles.id"), index=True, nullable=False)

    bookmark_user = relationship("User", back_populates="user_bookmark", lazy="noload")
    bookmark_mediafile = relationship("Mediafile", back_populates="mediafile_bookmark", lazy="noload")

    def __init__(self, user_id: int, mediafile_id: int):
        """Init model."""
        self.user_id = user_id
        self.mediafile_id = mediafile_id
