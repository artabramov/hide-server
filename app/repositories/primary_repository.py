"""Primary repository."""

from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager


class PrimaryRepository:
    """Primary repository."""

    def __init__(self, session, cache) -> None:
        """Init repository."""
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)

    async def commit(self):
        """Commit transaction."""
        await self.entity_manager.commit()

    async def rollback(self):
        """Rollback transaction."""
        await self.entity_manager.rollback()
