"""SQLAlchemy album models."""

from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.primary_model import Primary


class Album(Primary):
    """SQLAlchemy album model."""

    __tablename__ = "albums"

    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    is_locked = Column(Boolean, nullable=False, default=False, index=True)
    album_name = Column(String(128), nullable=False, index=True)
    album_description = Column(String(512), index=False, nullable=True)
    mediafiles_count = Column(Integer, index=True, nullable=False, default=0)
    mediafiles_size = Column(BigInteger, index=True, nullable=False, default=0)

    album_user = relationship("User", back_populates="user_album", lazy="joined")
    album_mediafile = relationship("Mediafile", back_populates="mediafile_album", lazy="noload")

    def __init__(self, user_id: int, is_locked: bool, album_name: str, album_description: str=None):
        """Init model."""
        self.user_id = user_id
        self.is_locked = is_locked
        self.album_name = album_name
        self.album_description = album_description
        self.mediafiles_count = 0
        self.mediafiles_size = 0

    def to_dict(self):
        """Get model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "is_locked": self.is_locked,
            "album_name": self.album_name,
            "album_description": self.album_description,
            "mediafiles_count": self.mediafiles_count,
            "mediafiles_size": self.mediafiles_size,
            "album_user": self.album_user.to_dict(),
        }
