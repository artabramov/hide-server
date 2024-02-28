"""Album Pydantic schemas."""

from pydantic import BaseModel, Field, SecretStr, validator
from fastapi import Query, File, UploadFile
from typing import Optional, List, Literal, Union
from app.models.user_model import UserRole
from fastapi.exceptions import RequestValidationError
from app.errors import E


class AlbumSchema(BaseModel):
    """Album Pydantic schema."""

    id: int
    created_date: int
    updated_date: int
    user_id: int
    album_name: str
    album_summary: Optional[str] = None
    mediafiles_count: int
    mediafiles_size: int
    user: dict


class AlbumInsertValidator(BaseModel):
    """Album insertion Pydantic schema."""

    is_locked: bool
    album_name: str = Query(min_length=1, max_length=128)
    album_summary: Optional[str] = Query(default=None, max_length=512)


class AlbumUpdateValidator(BaseModel):
    """Album updation Pydantic schema."""

    is_locked: bool
    album_name: str = Query(min_length=1, max_length=128)
    album_summary: Optional[str] = Query(default=None, max_length=512)


class AlbumsListValidator(BaseModel):
    """Albums list Pydantic schema."""

    album_name__ilike: Optional[str] = None
    offset: int = Query(ge=0)
    limit: int = Query(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "album_name", "mediafiles_count", "mediafiles_size"]
    order: Literal["asc", "desc"]
