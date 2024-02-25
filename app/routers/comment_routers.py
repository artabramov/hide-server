"""Comment routers."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from app.session import get_session
from app.cache import get_cache
from app.schemas.comment_schemas import CommentSchema, CommentInsertSchema, CommentSelectSchema, CommentUpdateSchema, CommentDeleteSchema, CommentsListSchema
from app.repositories.comment_repository import CommentRepository
from app.auth import auth_editor, auth_writer, auth_reader
from app.repositories.mediafile_repository import MediafileRepository
from app.models.comment_model import Comment
from app.errors import E

router = APIRouter()


@router.post("/comment", tags=["comments"])
async def insert_comment(session=Depends(get_session), cache=Depends(get_cache), schema=Depends(CommentInsertSchema),
                         current_user=Depends(auth_writer)):
    """Insert comment."""
    try:
        mediafile_repository = MediafileRepository(session, cache)
        mediafile = await mediafile_repository.select(schema.mediafile_id)
    except ValueError:
        raise RequestValidationError({"loc": ["query", "mediafile_id"], "input": schema.mediafile_id,
                                      "type": "value_invalid", "msg": E.VALUE_INVALID})

    comment_repository = CommentRepository(session, cache)
    await comment_repository.lock_all()
    comment = Comment(current_user.id, mediafile.id, schema.comment_content)
    comment = await comment_repository.insert(comment)

    mediafile.comments_count = await comment_repository.count_all(mediafile_id__eq=mediafile.id)
    await mediafile_repository.update(mediafile, commit=True)

    return {
        "comment_id": comment.id,
    }

@router.get("/comment/{comment_id}", tags=["comments"], response_model=CommentSchema)
async def select_comment(session=Depends(get_session), cache=Depends(get_cache), schema=Depends(CommentSelectSchema),
                         current_user=Depends(auth_reader)):
    """Select comment."""
    try:
        comment_repository = CommentRepository(session, cache)
        comment = await comment_repository.select(schema.comment_id)
    except ValueError:
        raise HTTPException(status_code=404)

    return comment.to_dict()


@router.put("/comment/{comment_id}", tags=["comments"])
async def update_comment(session=Depends(get_session), cache=Depends(get_cache), schema=Depends(CommentUpdateSchema),
                         current_user=Depends(auth_editor)):
    """Update comment."""
    try:
        comment_repository = CommentRepository(session, cache)
        comment = await comment_repository.select(schema.comment_id)
    except ValueError:
        raise HTTPException(status_code=404)
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403)

    comment.comment_content = schema.comment_content
    await comment_repository.update(comment, commit=True)
    return {}


@router.delete("/comment/{comment_id}", tags=["comments"])
async def delete_comment(session=Depends(get_session), cache=Depends(get_cache), schema=Depends(CommentDeleteSchema),
                         current_user=Depends(auth_editor)):
    """Delete comment."""
    try:
        comment_repository = CommentRepository(session, cache)
        comment = await comment_repository.select(schema.comment_id)
    except ValueError:
        raise HTTPException(status_code=404)

    if not current_user.can_admin or comment.user_id != current_user.id:
        raise HTTPException(status_code=403)

    await comment_repository.lock_all()
    await comment_repository.delete(comment)

    mediafile_repository = MediafileRepository(session, cache)
    mediafile = await mediafile_repository.select(comment.mediafile_id)
    mediafile.comments_count = await comment_repository.count_all(mediafile_id__eq=mediafile.id)
    await mediafile_repository.update(mediafile, commit=True)

    return {}


@router.get("/comments", tags=["comments"])
async def comments_list(session=Depends(get_session), cache=Depends(get_cache), schema=Depends(CommentsListSchema),
                        current_user=Depends(auth_reader)):
    """Comments list."""
    comment_repository = CommentRepository(session, cache)

    kwargs = {key[0]: key[1] for key in schema if key[1]}
    comments = await comment_repository.select_all(**kwargs)
    comments_count = await comment_repository.count_all(**kwargs)
    return {
        "comments": [comment.to_dict() for comment in comments],
        "comments_count": comments_count,
    }
