import asyncio
import sys
from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User, table_registry
from fast_zero.security import get_password_hash

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'#{obj.username}@')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.fixture
async def client(session: AsyncSession):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
async def engine():
    with PostgresContainer('postgres:16-alpine', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest.fixture
async def session(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


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
async def token(client: TestClient, user: User):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    return response.json()['access_token']
