from typing import Any, AsyncGenerator, Dict
from sqlalchemy import inspect

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declarative_base, sessionmaker

import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


class Base(DeclarativeBase):
    def _asdict(self) -> Dict[str, Any]:
        """
        Convert SQLAlchemy model object to a dict.

        :returns: A dict with column name as a key and value as column values.
        """
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncGenerator, None]:
    async with async_session_maker() as session:
        yield session
