"""Entity Manager."""

from sqlalchemy import asc, desc, text
from sqlalchemy.sql import func, exists
from sqlalchemy import select
from decimal import Decimal
from app.logger import get_log
import time

_ORDER_BY, _ORDER = "order_by", "order"
_ASC, _DESC = "asc", "desc"
_OFFSET, _LIMIT = "offset", "limit"
_SQLALCHEMY_RESERVED = [_OFFSET, _LIMIT, _ORDER_BY, _ORDER]
_SQLALCHEMY_OPERATORS = {
    "in": "in_",
    "eq": "__eq__",
    "not": "__ne__",
    "gte": "__ge__",
    "lte": "__le__",
    "gt": "__gt__",
    "lt": "__lt__",
    "like": "like",
    "ilike": "ilike",
}

log = get_log()



class EntityManager:
    """Entity Manager provides methods for working with SQLAlchemy objects in Postgres database."""

    def __init__(self, session) -> None:
        """Init Entity Manager."""
        self.session = session

    async def insert(self, obj: object, commit: bool=False) -> None:
        """Insert SQLAlchemy object into Postgres database."""
        start_time = time.time()

        self.session.add(obj)
        await self.session.flush()

        elapsed_time = time.time() - start_time
        log.debug("Insert into postgres, log_tag=postgres, elapsed_time=%s, cls=%s, obj=%s, commit=%s" % (
            elapsed_time, str(obj.__class__.__name__), str(obj.__dict__), commit))

        if commit:
            await self.commit()

    async def select(self, cls: object, obj_id: int) -> object:
        """Select SQLAlchemy object from Postgres database."""
        start_time = time.time()

        async_result = await self.session.execute(select(cls).where(cls.id == obj_id).limit(1))
        obj = async_result.unique().scalars().one_or_none()

        elapsed_time = time.time() - start_time
        log.debug("Select from postgres by id, log_tag=postgres, elapsed_time=%s, cls=%s, obj_id=%s, obj=%s" % (
            elapsed_time, str(cls.__name__), obj_id, str(obj.__dict__) if obj else None))

        return obj

    async def select_by(self, cls: object, **kwargs) -> object:
        """Select SQLAlchemy object from Postgres database."""
        start_time = time.time()

        async_result = await self.session.execute(select(cls).where(*self._where(cls, **kwargs)).limit(1))
        obj = async_result.unique().scalars().one_or_none()

        elapsed_time = time.time() - start_time
        log.debug("Select from postgres by kwargs, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, obj=%s." % (
            elapsed_time, str(cls.__name__), str(kwargs), obj))
        return obj

    async def update(self, obj: object, commit: bool = False) -> None:
        """Update SQLAlchemy object in Postgres database."""
        start_time = time.time()

        self.session.merge(obj)
        await self.session.flush()

        elapsed_time = time.time() - start_time
        log.debug("Update in postgres, log_tag=postgres, elapsed_time=%s, cls=%s, obj=%s." % (
            elapsed_time, str(obj.__class__.__name__), str(obj.__dict__)))

        if commit:
            await self.commit()

    async def delete(self, obj: object, commit: bool = False):
        """Delete SQLAlchemy object from Postgres database."""
        result = await self.session.delete(obj)

        log.debug("Delete from postgres, log_tag=postgres, cls=%s, obj=%s." % (
            str(obj.__class__.__name__), str(obj.__dict__)))

        if commit:
            await self.commit()

    async def select_all(self, cls: object, **kwargs) -> list:
        """Select a bunch of SQLAlchemy objects from Postgres database."""
        start_time = time.time()

        async_result = await self.session.execute(
            select(cls) \
            .where(*self._where(cls, **kwargs)) \
            .order_by(self._order_by(cls, **kwargs)) \
            .offset(self._offset(**kwargs)) \
            .limit(self._limit(**kwargs)))
        objs = async_result.unique().scalars().all()

        elapsed_time = time.time() - start_time
        log.debug("Select all from postgres, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, objs=%s" % (
            elapsed_time, str(cls.__name__), str(kwargs), str([obj.__dict__ for obj in objs])))

        return objs

    async def count_all(self, cls: object, **kwargs) -> int:
        """Count SQLAlchemy objects in Postgres database."""
        start_time = time.time()

        async_result = await self.session.execute(
            select(func.count()).select_from(select(cls).where(*self._where(cls, **kwargs))))
        result = async_result.unique().scalars().one_or_none()

        elapsed_time = time.time() - start_time
        log.debug("Count all in postgres, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, count=%s." % (
            elapsed_time, str(cls.__name__), str(kwargs), result))

        return result

    # async def sum_all(self, cls: object, column_name: str, **kwargs) -> Decimal:
    #     """Sum SQLAlchemy objects column in Postgres database."""
    #     query = self.session.query(func.sum(getattr(cls, column_name))).filter(*self._where(cls, **kwargs))
    #     res = query.one()[0]

    #     log.debug("Sum SQLAlchemy objects column in Postgres database, cls=%s, column_name=%s, kwargs=%s, sum=%s." % (
    #         str(cls.__name__), column_name, str(kwargs), res))

    #     return res

    async def exists(self, cls: object, **kwargs) -> bool:
        """Check if object exists in Postgres database."""
        start_time = time.time()

        async_result = await self.session.execute(select(cls).where(*self._where(cls, **kwargs)).limit(1))
        result = async_result.unique().scalars().one_or_none() is not None

        elapsed_time = time.time() - start_time
        log.debug("Exists in postgres, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, result=%s." % (
            elapsed_time, str(cls.__name__), str(kwargs), result))
        return result

    # async def subquery(self, cls, foreign_key, **kwargs):
    #     """Make a subquery expression for another class by a foreign key."""
    #     return self.session.query(getattr(cls, foreign_key)).filter(*self._where(cls, **kwargs))

    # async def exec(self, sql: str, commit: bool = False) -> object:
    #     """Execute a raw query."""
    #     res = self.db.engine.execute(text(sql))
    #     log.debug("Execute a raw query, sql=%s." % sql)

    #     if commit:
    #         await self.commit()

    #     return res

    async def commit(self) -> None:
        """Commit transaction."""
        await self.session.commit()
        log.debug("Commit transaction, log_tag=postgres.")

    async def rollback(self) -> None:
        """Rollback transaction."""
        await self.session.rollback()
        log.debug("Rollback transaction, log_tag=postgres.")

    def _where(self, cls, **kwargs):
        """Make WHERE statement."""
        where = []
        for key in {x: kwargs[x] for x in kwargs if x not in _SQLALCHEMY_RESERVED}:
            column_name, operator = key.split("__")

            if hasattr(cls, column_name):
                column = getattr(cls, column_name)

                value = kwargs[key]
                if isinstance(value, str):
                    if operator == "in":
                        value = [x.strip() for x in value.split(",")]
                    else:
                        value = value

                operation = getattr(column, _SQLALCHEMY_OPERATORS[operator])(value)
                where.append(operation)
        return where

    def _order_by(self, cls, **kwargs):
        """Make ORDER BY statement."""
        order_by = getattr(cls, kwargs.get(_ORDER_BY))
        return asc(order_by) if kwargs.get(_ORDER, _ASC) == _ASC else desc(order_by)

    def _offset(self, **kwargs):
        """Make OFFSET statement."""
        return kwargs.get(_OFFSET)

    def _limit(self, **kwargs):
        """Make LIMIT statement."""
        return kwargs.get(_LIMIT)
