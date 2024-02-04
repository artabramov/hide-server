import logging
from logging.handlers import RotatingFileHandler
from logging import Filter
from functools import lru_cache
from app.config import get_cfg
from app.context import get_ctx

cfg = get_cfg()
ctx = get_ctx()


class ContextualFilter(Filter):
    """Contextual filter for logging."""

    def filter(self, message: object) -> bool:
        """Customize the contextual filter."""
        message.trace_request_uuid = ctx.trace_request_uuid
        message.pid = ctx.pid
        return True


handler = RotatingFileHandler(filename=cfg.LOG_FILENAME, maxBytes=cfg.LOG_FILESIZE,
                                backupCount=cfg.LOG_FILES_LIMIT)
handler.setFormatter(logging.Formatter(cfg.LOG_FORMAT))

log = logging.getLogger(cfg.APP_NAME)
log.addHandler(handler)
log.addFilter(ContextualFilter())
log.setLevel(logging.getLevelName(cfg.LOG_LEVEL))
