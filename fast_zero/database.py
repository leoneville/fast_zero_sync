from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.settings import Settings

engine = create_async_engine(
    Settings().DATABASE_URL, connect_args={'check_same_thread': False}
)


async def get_session():  # pragma: no cover
    async with AsyncSession(engine) as session:
        yield session
