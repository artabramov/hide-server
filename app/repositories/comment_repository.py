"""Comment repository."""

from app.repositories.base_repository import BaseRepository
from app.models.comment_model import Comment


class CommentRepository(BaseRepository):
    """Comment repository."""

    async def insert(self, comment: Comment, commit: bool=False) -> Comment:
        """Insert comment."""
        await self.entity_manager.insert(comment, commit=commit)
        return comment

    async def select(self, comment_id: int) -> Comment:
        """Select comment."""
        comment = await self.cache_manager.get(Comment, comment_id)
        if not comment:
            comment = await self.entity_manager.select(Comment, comment_id)

        if not comment:
            raise ValueError

        await self.cache_manager.set(comment)
        return comment

    async def update(self, comment: Comment, commit: bool=False) -> Comment:
        """Update comment."""
        await self.entity_manager.update(comment, commit=commit)
        await self.cache_manager.delete(comment)
        return comment

    async def delete(self, comment: Comment, commit: bool=False) -> None:
        """Delete comment."""
        await self.entity_manager.delete(comment, commit=commit)
        await self.cache_manager.delete(comment)

    async def select_all(self, **kwargs) -> list:
        """Select comments."""
        comments = await self.entity_manager.select_all(Comment, **kwargs)
        for comment in comments:
            await self.cache_manager.set(comment)
        return comments

    async def count_all(self, **kwargs) -> int:
        """Count comments."""
        return await self.entity_manager.count_all(Comment, **kwargs)
