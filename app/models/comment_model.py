"""Comment SQLAlchemy model."""

from sqlalchemy import Column, BigInteger, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.basic_model import Basic


class Comment(Basic):
    """Comment SQLAlchemy model."""

    __tablename__ = "comments"

    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    mediafile_id = Column(BigInteger, ForeignKey('mediafiles.id'), index=True, nullable=False)
    comment_content = Column(Text, nullable=False)

    comment_user = relationship("User", back_populates="comment", lazy="joined")
    comment_mediafile = relationship("Mediafile", back_populates="comment", lazy="noload")

    def __init__(self, user_id: int, mediafile_id: int, comment_content: str):
        """Init Comment model."""
        self.user_id = user_id
        self.mediafile_id = mediafile_id
        self.comment_content = comment_content

    def to_dict(self):
        """Return Comment model as dictionary."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "mediafile_id": self.mediafile_id,
            "comment_content": self.comment_content,
            "comment_user": self.comment_user.to_dict(),
        }
