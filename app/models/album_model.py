"""Album SQLAlchemy model."""

from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.basic_model import Basic



class Album(Basic):
    """Album SQLAlchemy model."""

    __tablename__ = "albums"

    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    album_name = Column(String(128), nullable=False, index=True)
    album_summary = Column(String(512), index=False, nullable=True)
    mediafiles_count = Column(Integer, index=True, nullable=False, default=0)
    mediafiles_size = Column(BigInteger, index=True, nullable=False, default=0)

    user = relationship("User", back_populates="album", lazy="joined")
    mediafile = relationship("Mediafile", back_populates="mediafile_album", lazy="noload")

    def __init__(self, user_id: int, is_locked: bool, album_name: str, album_summary: str=None):
        """Initialize model."""
        self.user_id = user_id
        self.is_locked = is_locked
        self.album_name = album_name
        self.album_summary = album_summary
        self.mediafiles_count = 0
        self.mediafiles_size = 0

    def to_dict(self):
        """Return model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "is_locked": self.is_locked,
            "album_name": self.album_name,
            "album_summary": self.album_summary,
            "mediafiles_count": self.mediafiles_count,
            "mediafiles_size": self.mediafiles_size,
            "user": self.user.to_dict(),
        }
