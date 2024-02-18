"""User and related SQLAlchemy models."""

import enum
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.session import Base
from app.config import get_cfg

cfg = get_cfg()


mediafiles_tags = Table("mediafiles_tags", Base.metadata,
                    Column("id", BigInteger, primary_key=True, index=True),
                    Column("created_date", Integer, nullable=False, index=True, default=lambda: int(time())),
                    Column("mediafile_id", Integer, ForeignKey("mediafiles.id"), index=True),
                    Column("tag_id", Integer, ForeignKey("tags.id"), index=True)
                )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True, index=True)
    created_date = Column(Integer, nullable=False, index=True, default=lambda: int(time()))
    tag_value = Column(String(128), nullable=False, unique=True)

    mediafiles = relationship("Mediafile", secondary=mediafiles_tags, back_populates="tags", lazy="noload")

    def __init__(self, tag_value: str):
        """Init user SQLAlchemy object."""
        self.tag_value = tag_value
