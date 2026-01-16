from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from database import get_session
from models import User, table_registry
from security import get_hashed_password
from settings import Settings
from src.app import app


@pytest.fixture
def client(session):
    def _override_get_session():
        return session

    app.dependency_overrides[get_session] = _override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


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

    user = User(
        username='testuser',
        email='testuser@example.com',
        password=get_hashed_password(password),
    )

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
