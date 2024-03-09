"""Pydantic comment schemas."""

from pydantic import BaseModel
from fastapi import Query
from typing import Literal


class CommentSchema(BaseModel):
    """Pydantic comment schema."""

    id: int
    created_date: int
    updated_date: int
    user_id: int
    mediafile_id: int
    comment_content: str
    comment_user: dict


class CommentInsertSchema(BaseModel):
    """Pydantic comment insertion schema."""

    mediafile_id: int
    comment_content: str = Query(min_length=1, max_length=512)


class CommentSelectSchema(BaseModel):
    """Pydantic comment selection schema."""

    comment_id: int = Query(ge=1)


class CommentUpdateSchema(BaseModel):
    """Pydantic comment updation schema."""

    comment_id: int = Query(ge=1)
    comment_content: str


class CommentDeleteSchema(BaseModel):
    """Comment deletion Pydantic schema."""

    comment_id: int = Query(ge=1)


class CommentsListSchema(BaseModel):
    """Comments list Pydantic schema."""

    mediafile_id__eq: int = Query(ge=1)
    offset: int = Query(ge=0)
    limit: int = Query(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]
