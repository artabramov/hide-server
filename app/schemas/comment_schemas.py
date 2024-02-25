"""Comment Pydantic schemas."""

from pydantic import BaseModel
from fastapi import Query
from typing import Literal


class CommentSchema(BaseModel):
    """Comment Pydantic schema."""

    id: int
    created_date: int
    updated_date: int
    user_id: int
    mediafile_id: int
    comment_content: str
    comment_user: dict


class CommentInsertSchema(BaseModel):
    """Comment insertion Pydantic schema."""

    mediafile_id: int = Query(ge=1)
    comment_content: str


class CommentSelectSchema(BaseModel):
    """Comment selection Pydantic schema."""

    comment_id: int = Query(ge=1)


class CommentUpdateSchema(BaseModel):
    """Comment updation Pydantic schema."""

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
