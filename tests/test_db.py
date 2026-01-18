import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_async.models import User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test',
            email='test@test.com',
            password='secret',
        )

        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'test'))

    assert user is not None
    assert user.id == 1
    assert user.username == 'test'
    assert user.email == 'test@test.com'
    assert user.created_at == time
    assert user.todos == []
