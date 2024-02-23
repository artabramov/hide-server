"""Cache manager."""

from sqlalchemy.ext.serializer import dumps, loads
from app.config import get_cfg
from app.decorators.timed_deco import timed

cfg = get_cfg()


class CacheManager:
    """Cache Manager provides methods for working with Redis cache."""

    def __init__(self, cache) -> None:
        """Init Cache Manager."""
        self.cache = cache

    @timed
    async def set(self, obj: object) -> None:
        """Insert SQLAlchemy object in Redis cache."""
        await self.cache.set('%s:%s' % (obj.__tablename__, obj.id), dumps(obj), ex=cfg.REDIS_EXPIRE)

    @timed
    async def get(self, cls: object, obj_id: int) -> object:
        """Select SQLAlchemy object from Redis cache."""
        obj_bytes = await self.cache.get('%s:%s' % (cls.__tablename__, obj_id))
        return loads(obj_bytes) if obj_bytes else None

    @timed
    async def delete(self, obj: object):
        """Delete SQLAlchemy object from Redis cache."""
        await self.cache.delete('%s:%s' % (obj.__tablename__, obj.id))
