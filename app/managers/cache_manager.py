"""Cache manager."""

from sqlalchemy.ext.serializer import dumps, loads
from app.logger import get_log
from app.config import get_cfg
from time import time
from concurrent.futures import Future

cfg = get_cfg()
log = get_log()


class CacheManager:
    """Cache Manager provides methods for working with Redis cache."""

    def __init__(self, cache) -> None:
        """Init Cache Manager."""
        self.cache = cache

    async def set(self, obj: object) -> None:
        """Insert SQLAlchemy object in Redis cache."""
        start_time = time()

        res = await self.cache.set('%s:%s' % (obj.__tablename__, obj.id), dumps(obj), ex=cfg.REDIS_EXPIRE)
        
        log.debug("Insert into redis, log_tag=redis, elapsed_time=%s, cls=%s, obj=%s, res=%s." % (
            time() - start_time, str(obj.__class__.__name__), str(obj.__dict__), res))

    async def get(self, cls: object, obj_id: int) -> object:
        """Select SQLAlchemy object from Redis cache."""
        start_time = time()

        obj_bytes = await self.cache.get('%s:%s' % (cls.__tablename__, obj_id))
        obj = loads(obj_bytes) if obj_bytes else None

        log.debug("Select from redis, log_tag=redis, elapsed_time=%s, cls=%s, obj_id=%s, obj=%s." % (
            time() - start_time, str(cls.__name__), obj_id, str(obj.__dict__) if obj else None))
        return obj

    async def delete(self, obj: object):
        """Delete SQLAlchemy object from Redis cache."""
        start_time = time()

        res = await self.cache.delete('%s:%s' % (obj.__tablename__, obj.id))

        log.debug("Delete from redis, log_tag=redis, elapsed_time=%s, cls=%s, obj_id=%s, res=%s." % (
            time() - start_time, str(obj.__class__.__name__), str(obj.__dict__), res))
