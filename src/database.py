from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from settings import Settings

_engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():  # pragma: no cover
    async with AsyncSession(_engine, expire_on_commit=False) as session:
        yield session
