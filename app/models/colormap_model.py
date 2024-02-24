"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


class Colormap(Base):
    """SQLAlchemy model for album."""

    __tablename__ = "colormaps"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()))
    mediafile_id = Column(BigInteger, ForeignKey('mediafiles.id'), index=True, nullable=False)
    maroon = Column(Numeric, nullable=False, default=0)
    red = Column(Numeric, nullable=False, default=0)
    orange = Column(Numeric, nullable=False, default=0)
    yellow = Column(Numeric, nullable=False, default=0)
    olive = Column(Numeric, nullable=False, default=0)
    green = Column(Numeric, nullable=False, default=0)
    lime = Column(Numeric, nullable=False, default=0)
    teal = Column(Numeric, nullable=False, default=0)
    aqua = Column(Numeric, nullable=False, default=0)
    blue = Column(Numeric, nullable=False, default=0)
    navy = Column(Numeric, nullable=False, default=0)
    fuchsia = Column(Numeric, nullable=False, default=0)
    purple = Column(Numeric, nullable=False, default=0)
    black = Column(Numeric, nullable=False, default=0)
    gray = Column(Numeric, nullable=False, default=0)
    silver = Column(Numeric, nullable=False, default=0)
    white = Column(Numeric, nullable=False, default=0)

    mediafile = relationship("Mediafile", back_populates="colormap", lazy="noload")

    def __init__(self, mediafile_id: int, maroon: float = 0, red: float = 0, orange: float = 0, yellow: float = 0,
                 olive: float = 0, green: float = 0, lime: float = 0, teal: float = 0, aqua: float = 0, blue: float = 0,
                 navy: float = 0, fuchsia: float = 0, purple: float = 0, black: float = 0, gray: float = 0,
                 silver: float = 0, white: float = 0):
        """Init user SQLAlchemy object."""
        self.mediafile_id = mediafile_id
        self.maroon = maroon
        self.red = red
        self.orange = orange
        self.yellow = yellow
        self.olive = olive
        self.green = green
        self.lime = lime
        self.teal = teal
        self.aqua = aqua
        self.blue = blue
        self.navy = navy
        self.fuchsia = fuchsia
        self.purple = purple
        self.black = black
        self.gray = gray
        self.silver = silver
        self.white = white

    # def to_dict(self):
    #     """Return model as dict."""
    #     return {
    #         "id": self.id,
    #         "created_date": self.created_date,
    #         "updated_date": self.updated_date,
    #         "user_id": self.user_id,
    #         "album_name": self.album_name,
    #         "album_summary": self.album_summary,
    #         "mediafiles_count": self.mediafiles_count,
    #         "mediafiles_size": self.mediafiles_size,
    #         "user": self.user.to_dict(),
    #     }
