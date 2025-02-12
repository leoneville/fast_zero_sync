from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='neville',
            email='leo@ville.com',
            password='minha_senha-123',
        )
        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'neville')
        )

        assert asdict(user) == {
            'id': 1,
            'username': 'neville',
            'password': 'minha_senha-123',
            'email': 'leo@ville.com',
            'created_at': time,
            'updated_at': time,
            'todos': [],
        }


@pytest.mark.asyncio
async def test_create_todo(session: AsyncSession, user: User, mock_db_time):
    with mock_db_time(model=Todo) as time:
        todo = Todo(
            title='Test Todo',
            description='Test Desc',
            state='draft',
            user_id=user.id,
        )

        session.add(todo)
        await session.commit()

        todo = await session.scalar(select(Todo))

        assert asdict(todo) == {
            'description': 'Test Desc',
            'id': 1,
            'state': 'draft',
            'title': 'Test Todo',
            'user_id': 1,
            'created_at': time,
            'updated_at': time,
        }


@pytest.mark.asyncio
async def test_user_todo_relationship(session: AsyncSession, user: User):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
