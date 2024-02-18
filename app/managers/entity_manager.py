"""Entity Manager."""

from sqlalchemy import asc, desc, text
from sqlalchemy.sql import func, exists
from sqlalchemy import select
from decimal import Decimal
from app.logger import get_log
from time import time

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
        start_time = time()

        self.session.add(obj)
        await self.session.flush()

        log.debug("Insert into postgres, log_tag=postgres, elapsed_time=%s, cls=%s, obj=%s, commit=%s." % (
            time() - start_time, str(obj.__class__.__name__), str(obj.__dict__), commit))

        if commit:
            await self.commit()

    async def select(self, cls: object, obj_id: int) -> object:
        """Select SQLAlchemy object from Postgres database."""
        start_time = time()

        async_result = await self.session.execute(select(cls).where(cls.id == obj_id).limit(1))
        obj = async_result.unique().scalars().one_or_none()

        log.debug("Select from postgres by id, log_tag=postgres, elapsed_time=%s, cls=%s, obj_id=%s, obj=%s." % (
            time() - start_time, str(cls.__name__), obj_id, str(obj.__dict__) if obj else None))

        return obj

    async def select_by(self, cls: object, **kwargs) -> object:
        """Select SQLAlchemy object from Postgres database."""
        start_time = time()

        async_result = await self.session.execute(select(cls).where(*self._where(cls, **kwargs)).limit(1))
        obj = async_result.unique().scalars().one_or_none()

        log.debug("Select from postgres by kwargs, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, obj=%s." % (
            time() - start_time, str(cls.__name__), str(kwargs), obj))
        return obj

    async def update(self, obj: object, commit: bool = False) -> None:
        """Update SQLAlchemy object in Postgres database."""
        start_time = time()

        await self.session.merge(obj)
        await self.session.flush()

        log.debug("Update in postgres, log_tag=postgres, elapsed_time=%s, cls=%s, obj=%s." % (
            time() - start_time, str(obj.__class__.__name__), str(obj.__dict__)))

        if commit:
            await self.commit()

    async def delete(self, obj: object, commit: bool = False):
        """Delete SQLAlchemy object from Postgres database."""
        start_time = time()

        res = await self.session.delete(obj)

        log.debug("Delete from postgres, log_tag=postgres, elapsed_time=%s, cls=%s, obj=%s, res=%s." % (
            time() - start_time, str(obj.__class__.__name__), str(obj.__dict__), res))

        if commit:
            await self.commit()

    async def select_all(self, cls: object, **kwargs) -> list:
        """Select a bunch of SQLAlchemy objects from Postgres database."""
        start_time = time()

        async_result = await self.session.execute(
            select(cls) \
            .where(*self._where(cls, **kwargs)) \
            .order_by(self._order_by(cls, **kwargs)) \
            .offset(self._offset(**kwargs)) \
            .limit(self._limit(**kwargs)))
        objs = async_result.unique().scalars().all()

        log.debug("Select all from postgres, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, objs=%s." % (
            time() - start_time, str(cls.__name__), str(kwargs), str([obj.__dict__ for obj in objs])))

        return objs

    async def count_all(self, cls: object, **kwargs) -> int:
        """Count SQLAlchemy objects in Postgres database."""
        start_time = time()

        async_result = await self.session.execute(
            select(func.count(getattr(cls, "id"))).where(*self._where(cls, **kwargs)))
        res = async_result.unique().scalars().one_or_none() or 0

        log.debug("Count all in postgres, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, res=%s." % (
            time() - start_time, str(cls.__name__), str(kwargs), res))

        return res

    async def sum_all(self, cls: object, column: str, **kwargs):
        """Sum SQLAlchemy object column in Postgres database."""
        start_time = time()

        async_result = await self.session.execute(
            select(func.sum(getattr(cls, column))).where(*self._where(cls, **kwargs)))
        res = async_result.unique().scalars().one_or_none() or 0

        log.debug("Sum all in postgres, log_tag=postgres, elapsed_time=%s, cls=%s, column=%s, kwargs=%s, res=%s." % (
            time() - start_time, str(cls.__name__), column, str(kwargs), res))

        return res

    async def exists(self, cls: object, **kwargs) -> bool:
        """Check if object exists in Postgres database."""
        start_time = time()

        async_result = await self.session.execute(select(cls).where(*self._where(cls, **kwargs)).limit(1))
        res = async_result.unique().scalars().one_or_none() is not None

        log.debug("Exists in postgres, log_tag=postgres, elapsed_time=%s, cls=%s, kwargs=%s, res=%s." % (
            time() - start_time, str(cls.__name__), str(kwargs), res))
        return res

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
        start_time = time()

        res = await self.session.commit()

        log.debug("Commit transaction, log_tag=postgres, elapsed_time=%s, res=%s." % (
            time() - start_time, res))

    async def rollback(self) -> None:
        """Rollback transaction."""
        start_time = time()

        res = await self.session.rollback()

        log.debug("Rollback transaction, log_tag=postgres, elapsed_time=%s, res=%s." % (
            time() - start_time, res))

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
                    elif operator in ["like", "ilike"]:
                        value = "%" + value + "%"
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
