"""Basic SQLAlchemy model."""

from time import time
from sqlalchemy import Column, Integer, BigInteger
from sqlalchemy.orm import mapped_column
from app.session import Base


class Basic(Base):
    """Basic SQLAlchemy model."""

    __abstract__ = True

    id = mapped_column(BigInteger, primary_key=True, index=True, sort_order=-3)
    created_date = mapped_column(Integer, nullable=False, index=True, default=lambda: int(time()), sort_order=-2)
    updated_date = mapped_column(Integer, nullable=False, index=True, default=0, onupdate=lambda: int(time()), sort_order=-1)
