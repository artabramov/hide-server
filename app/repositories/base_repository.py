"""Comment repository."""

from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager


class BaseRepository:
    """Base repository."""

    def __init__(self, session, cache) -> None:
        """Init repository."""
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)

    async def commit(self):
        await self.entity_manager.commit()

    async def rollback(self):
        await self.entity_manager.rollback()
