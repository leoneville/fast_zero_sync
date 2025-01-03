import factory
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash
from fast_zero.settings import Settings


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'#{obj.username}@')


@pytest.fixture
async def ac(session: AsyncSession):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=Settings().BASE_URL
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
async def user(session: AsyncSession) -> User:
    pwd = 'testtest'
    user = UserFactory(
        password=get_password_hash(pwd),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = pwd  # Monkey Patch

    return user


@pytest.fixture
async def other_user(session: AsyncSession) -> User:
    other_user = UserFactory()
    session.add(other_user)
    await session.commit()
    await session.refresh(other_user)

    return other_user


@pytest.fixture
async def token(ac: AsyncClient, user: User):
    response = await ac.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    return response.json()['access_token']
