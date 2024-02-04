"""Asyncio session management."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, async_sessionmaker
from asyncio import current_task
from app.config import get_cfg

cfg = get_cfg()
Base = declarative_base()

connection_string = "postgresql+asyncpg://%s:%s@%s:%s/%s" % (
    cfg.POSTGRES_USERNAME, cfg.POSTGRES_PASSWORD, cfg.POSTGRES_HOST, cfg.POSTGRES_PORT, cfg.POSTGRES_DATABASE)

async_engine = create_async_engine(connection_string, echo=True, future=True)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session():
    """Return SQLAlchemy session object."""
    try:
        async_session = async_scoped_session(async_session_factory, scopefunc=current_task)
        session = async_session()
        yield session
    finally:
        await session.close()
        pass
