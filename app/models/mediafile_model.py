"""SQLAlchemy mediafile models."""

from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from app.managers.image_manager import ImageManager
from sqlalchemy.orm import relationship
from app.models.tag_model import MediafileTag
from app.config import get_cfg
import os
from app.models.primary_model import Primary
from app.mixins.fernet_mixin import FernetMixin

cfg = get_cfg()


class Mediafile(Primary, FernetMixin):
    """SQLAlchemy mediafile model."""

    __tablename__ = "mediafiles"
    _mediafile_path = None
    _mediafile_image = None
    _thumbnail_path = None
    _thumbnail_image = None

    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    album_id = Column(BigInteger, ForeignKey("albums.id"), index=True, nullable=False)

    mimetype = Column(String(512), nullable=False, index=True)
    filesize = Column(BigInteger, nullable=False, index=True)
    width = Column(Integer, nullable=False, index=True)
    height = Column(Integer, nullable=False, index=True)
    format = Column(String(40), nullable=False, index=True)
    mode = Column(String(40), nullable=False, index=True)

    original_filename = Column(String(512), nullable=False, index=True)
    mediafile_filename = Column(String(512), nullable=False, unique=True)
    thumbnail_filename = Column(String(512), nullable=False, unique=True)
    mediafile_description = Column(String(512), index=False, nullable=True)
    comments_count = Column(Integer, index=True, nullable=False, default=0)

    mediafile_user = relationship("User", back_populates="mediafile", lazy="joined")
    mediafile_album = relationship("Album", back_populates="album_mediafile", lazy="joined")
    mediafile_metadata = relationship("Metadata", back_populates="mediafile", lazy="joined", cascade="all,delete")
    mediafile_colorset = relationship("Colorset", back_populates="mediafile", lazy="joined", uselist=False, cascade="all,delete")
    mediafile_tags = relationship("Tag", secondary=MediafileTag.__table__, back_populates="mediafiles", lazy="joined")

    mediafile_comment = relationship("Comment", back_populates="comment_mediafile", lazy="noload", cascade="all,delete")

    def __init__(self, user_id: int, album_id: int, original_filename: str, mediafile_filename: str,
                 thumbnail_filename: str, mimetype: str, filesize: int, mediafile_description: str = None):
        """Init model."""
        self.user_id = user_id
        self.album_id = album_id
        self.original_filename = original_filename
        self.mediafile_filename = mediafile_filename
        self.thumbnail_filename = thumbnail_filename
        self.mediafile_description = mediafile_description
        self.comments_count = 0

        self.mimetype = mimetype
        self.filesize = filesize
        self.width = self.mediafile_image.width
        self.height = self.mediafile_image.height
        self.format = self.mediafile_image.format
        self.mode = self.mediafile_image.mode

    @property
    def mediafile_path(self):
        """Mediafile path."""
        if not self._mediafile_path:
            self._mediafile_path = os.path.join(cfg.MEDIAFILE_PATH, self.mediafile_filename)
        return self._mediafile_path

    @property
    def mediafile_image(self):
        """Mediafile image."""
        if not self._mediafile_image:
            self._mediafile_image = ImageManager.open_image(self.mediafile_path)
        return self._mediafile_image

    @property
    def thumbnail_path(self):
        """Thumbnail path."""
        if not self._thumbnail_path and self.thumbnail_filename:
            self._thumbnail_path = os.path.join(cfg.THUMBNAIL_PATH, self.thumbnail_filename)
        return self._thumbnail_path

    @property
    def thumbnail_image(self):
        """Thumbnail image."""
        if not self._thumbnail_image and self.thumbnail_filename:
            self._thumbnail_image = ImageManager.open_image(self.thumbnail_path)
        return self._thumbnail_image

    async def encrypt(self):
        """Encrypt original file."""
        await self.encrypt_file(self.mediafile_path)

    async def decrypt(self):
        """Decrypt original file."""
        return await self.decrypt_file(self.mediafile_path)

    def to_dict(self):
        """Get model as dict."""
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "album_id": self.album_id,

            "mimetype": self.mimetype,
            "filesize": self.filesize,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "mode": self.mode,

            "original_filename": self.original_filename,
            "mediafile_image": cfg.MEDIAFILE_URL + self.mediafile_filename,
            "thumbnail_image": cfg.THUMBNAIL_URL + self.thumbnail_filename if self.thumbnail_filename else None,
            "mediafile_description": self.mediafile_description,
            "comments_count": self.comments_count,

            "mediafile_metadata": {x.meta_key: x.meta_value for x in self.mediafile_metadata},
            "mediafile_colorset": self.mediafile_colorset.to_dict() if self.mediafile_colorset else {},
            "mediafile_tags": [x.tag_value for x in self.mediafile_tags],
        }
