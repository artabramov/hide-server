"""Pydantic schemas for user model."""

from pydantic import BaseModel, Field, SecretStr, validator
from fastapi import Query, File, UploadFile
from typing import Optional, List, Literal, Union


class MediafileInsertValidator(BaseModel):
    """Pydantic schema for userpic uploading request."""

    album_id: int
    mediafile_description: Optional[str] = Query(default=None, max_length=512)
    file: UploadFile = File(...)


class MediafileUpdateValidator(BaseModel):
    """Pydantic schema for user registration request."""

    album_id: int
    original_filename: str = Query(..., min_length=1, max_length=512)
    mediafile_description: Optional[str] = Query(default=None, max_length=512)


class MediafilesListValidator(BaseModel):
    """Pydantic schema for users list request."""

    album_id: Optional[int] = None
    original_filename__ilike: Optional[str] = None
    offset: int = 0
    limit: int = Query(..., ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "original_filename"] = "id"
    order: Literal["asc", "desc"] = "desc"
