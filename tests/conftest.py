from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer


from fastapi_async.database import get_session
from fastapi_async.models import Todo, TodoState, User, table_registry
from fastapi_async.security import get_hashed_password
from fastapi_async.settings import Settings
from fastapi_async.app import app


@pytest.fixture
def client(session):
    def _override_get_session():
        return session

    app.dependency_overrides[get_session] = _override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer(
        'postgres:13.1-alpine',
        driver='psycopg',
    ) as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = 'securepassword123'

    user = UserFactory(password=get_hashed_password(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def another_user(session: AsyncSession):
    password = 'anothersecurepassword123'

    user = UserFactory(password=get_hashed_password(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    payload = {
        'username': user.username,
        'password': user.clean_password,
    }

    response = client.post('/auth/token', data=payload)
    response_data = response.json()

    return response_data['access_token']


@pytest.fixture
def settings():
    return Settings()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyFunction(lambda: 'securepassword123')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Sequence(lambda n: f'Todo Title {n}')
    description = factory.Faker('sentence')
    state = factory.fuzzy.FuzzyChoice(TodoState)

    user_id = 1
