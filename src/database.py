from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declarative_base
from typing import AsyncGenerator

import settings


DATABASE_URL = f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'


# class Base(DeclarativeBase):
#     pass
Base = declarative_base()

engine = create_async_engine(
    DATABASE_URL
)

async_session_maker = sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncGenerator, None]:
    async with async_session_maker() as session:
        yield session
