"""Pydantic mediafile schemas."""

from pydantic import BaseModel
from fastapi import Query, File, UploadFile
from typing import Optional, Literal
from app.schemas.primary_schema import PrimarySchema


class MediafileSchema(BaseModel):
    """Pydantic album schema."""

    id: int
    created_date: int
    updated_date: int
    user_id: int
    album_id: int

    mimetype: str
    filesize: int
    width: int
    height: int
    format: str
    mode: str

    original_filename: str
    mediafile_image: str
    thumbnail_image: Optional[str] = None
    mediafile_description: Optional[str] = None
    comments_count: int

    mediafile_metadata: dict
    mediafile_colorset: dict
    mediafile_tags: list


class MediafileInsertSchema(BaseModel):
    """Pydantic mediafile insertion schema."""

    album_id: int
    mediafile_description: Optional[str] = Query(default=None, max_length=512)
    file: UploadFile = File(...)


class MediafileUpdateSchema(BaseModel):
    """Pydantic mediafile updation schema."""

    album_id: int
    original_filename: str = Query(min_length=1, max_length=512)
    mediafile_description: Optional[str] = Query(default=None, max_length=512)


class MediafilesListSchema(PrimarySchema):
    """Pydantic mediafiles list schema."""

    album_id__eq: Optional[int] = None
    original_filename__ilike: Optional[str] = None
    offset: int = Query(ge=0)
    limit: int = Query(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "original_filename"]
    order: Literal["asc", "desc"]
