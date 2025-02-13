from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models import Todo, TodoState
from tests.factories import TodoFactory


def test_create_todo(
    client: TestClient,
    token,
    mock_db_time,
):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test todo',
                'description': 'Test todo description',
                'state': 'draft',
            },
        )
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {
            'id': 1,
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
        }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    client: TestClient, session: AsyncSession, user, token
):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    client: TestClient, session: AsyncSession, user, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('filter_field', 'filter_value'),
    [
        ('title', 'Test todo 1'),
        ('description', 'description'),
        ('state', 'draft'),
    ],
)
async def test_list_todos_filter(  # noqa
    client: TestClient,
    session: AsyncSession,
    user,
    token,
    filter_field,
    filter_value,
):
    expected_todos = 5
    todos_map = {
        'title': TodoFactory.create_batch(
            5, user_id=user.id, title=filter_value
        ),
        'description': TodoFactory.create_batch(
            5, user_id=user.id, description=filter_value
        ),
        'state': TodoFactory.create_batch(
            5, user_id=user.id, state=TodoState.draft
        ),
    }

    session.add_all(todos_map[filter_field])
    await session.commit()

    response = client.get(
        f'/todos/?{filter_field}={filter_value}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    client: TestClient, session: AsyncSession, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_delete_todo(
    client: TestClient, session: AsyncSession, user, token
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


def test_delete_todo_error(client: TestClient, token):
    response = client.delete(
        '/todos/490',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo(
    client: TestClient, session: AsyncSession, user, token
):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_patch_todo_error(client: TestClient, token):
    response = client.patch(
        '/todos/490',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_list_todos_should_return_all_expected_fields(  # noqa
    client: TestClient, session: AsyncSession, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

        await session.refresh(todo)
        response = client.get(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.json()['todos'] == [
            {
                'created_at': time.isoformat(),
                'updated_at': time.isoformat(),
                'description': todo.description,
                'id': todo.id,
                'state': todo.state,
                'title': todo.title,
            }
        ]
