"""Favorite repository."""

from app.repositories.primary_repository import PrimaryRepository
from app.models.favorite_model import Favorite


class FavoriteRepository(PrimaryRepository):
    """Favorite repository."""

    async def insert(self, user_id: int, mediafile_id: int, commit: bool=False) -> Favorite:
        """Insert favorite."""
        favorite = Favorite(user_id, mediafile_id)
        await self.entity_manager.insert(favorite, commit=commit)
        return favorite

    async def delete_all(self, commit: bool=False, **kwargs):
        """Delete all comments."""
        await self.entity_manager.delete_all(Favorite, commit=commit, **kwargs)
