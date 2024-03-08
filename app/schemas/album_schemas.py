"""Pydantic album schemas."""

from pydantic import BaseModel
from fastapi import Query
from typing import Optional, Literal
from app.schemas.primary_schema import PrimarySchema


class AlbumSchema(BaseModel):
    """Pydantic album schema."""

    id: int
    created_date: int
    updated_date: int
    user_id: int
    is_locked: bool
    album_name: str
    album_description: Optional[str] = None
    mediafiles_count: int
    mediafiles_size: int
    album_user: dict


class AlbumInsertSchema(BaseModel):
    """Pydantic album insertion schema."""

    is_locked: bool
    album_name: str = Query(min_length=1, max_length=128)
    album_description: Optional[str] = Query(default=None, max_length=512)


class AlbumUpdateSchema(BaseModel):
    """Pydantic album updation schema."""

    is_locked: bool
    album_name: str = Query(min_length=1, max_length=128)
    album_description: Optional[str] = Query(default=None, max_length=512)


class AlbumsListSchema(PrimarySchema):
    """Pydantic albums list schema."""

    album_name__ilike: Optional[str] = None
    offset: int = Query(ge=0)
    limit: int = Query(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id", "album_name", "mediafiles_count", "mediafiles_size"]
    order: Literal["asc", "desc"]
