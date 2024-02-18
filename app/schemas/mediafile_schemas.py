"""Pydantic schemas for user model."""

from pydantic import BaseModel, Field, SecretStr, validator
from fastapi import Query, File, UploadFile
from typing import Optional, List, Literal, Union
from fastapi.exceptions import RequestValidationError
from app.errors import E


class MediafileUploadSchema(BaseModel):
    """Pydantic schema for userpic uploading request."""

    album_id: int
    file: UploadFile = File(...)


class MediafileUpdateSchema(BaseModel):
    """Pydantic schema for user registration request."""

    album_id: int
    mediafile_name: str = Query(..., min_length=1, max_length=512)
    mediafile_summary: Optional[str] = Query(default=None, max_length=512)


class MediafilesListSchema(BaseModel):
    """Pydantic schema for users list request."""

    album_id: Optional[int] = None
    mediafile_name__ilike: Optional[str] = None
    offset: int = 0
    limit: int = Query(..., ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "mediafile_name"] = "id"
    order: Literal["asc", "desc"] = "desc"
