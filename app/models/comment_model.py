"""SQLAlchemy comment model."""

from sqlalchemy import Column, BigInteger, ForeignKey, String
from sqlalchemy.orm import relationship
from app.models.primary_model import Primary


class Comment(Primary):
    """SQLAlchemy comment model."""

    __tablename__ = "comments"

    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    mediafile_id = Column(BigInteger, ForeignKey("mediafiles.id"), index=True, nullable=False)
    comment_content = Column(String(512), index=False, nullable=False)

    comment_user = relationship("User", back_populates="comment", lazy="joined")
    comment_mediafile = relationship("Mediafile", back_populates="mediafile_comment", lazy="noload")

    def __init__(self, user_id: int, mediafile_id: int, comment_content: str):
        """Init model."""
        self.user_id = user_id
        self.mediafile_id = mediafile_id
        self.comment_content = comment_content

    def to_dict(self) -> dict:
        """Get model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "mediafile_id": self.mediafile_id,
            "comment_content": self.comment_content,
            "comment_user": self.comment_user.to_dict(),
        }
