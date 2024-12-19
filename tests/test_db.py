import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models import User


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_create_user(anyio_backend, session: AsyncSession):
    user = User(
        username='neville',
        email='leo@ville.com',
        password='minha_senha-123',
    )
    session.add(user)
    await session.commit()

    result = await session.scalar(
        select(User).where(User.email == 'leo@ville.com')
    )

    assert result.username == 'neville'
