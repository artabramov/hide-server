"""Pydantic schemas for user model."""

from pydantic import BaseModel, Field, SecretStr, validator
from fastapi import Query, File, UploadFile
from typing import Optional, List, Literal, Union
from app.models.user_models import UserRole
from fastapi.exceptions import RequestValidationError
from app.errors import E


class AlbumSchema(BaseModel):
    """Pydantic schema for user selection response."""

    id: int
    created_date: int
    updated_date: int
    user_id: int
    album_name: str
    album_summary: str
    mediafiles_count: int
    mediafiles_size: int
    user: dict


class AlbumEditSchema(BaseModel):
    """Pydantic schema for user registration request."""

    album_name: str = Query(..., min_length=1, max_length=128)
    album_summary: Optional[str] = Query(default=None, max_length=512)



