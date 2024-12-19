from http import HTTPStatus

import pytest
from httpx import AsyncClient

from fast_zero.schemas import UserPublic


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_root_deve_retornar_ok_e_ola_mundo(
    anyio_backend, ac: AsyncClient
):
    response = await ac.get('/')  # Act (ação)

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Olá Mundo!'}  # assert


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_create_user(anyio_backend, ac: AsyncClient):
    payload = {
        'username': 'neville',
        'email': 'neville@example.com',
        'password': 'thisismypassword',
    }

    response = await ac.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'neville',
        'email': 'neville@example.com',
    }


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_users(anyio_backend, ac: AsyncClient):
    response = await ac.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_users_with_user(anyio_backend, ac: AsyncClient, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await ac.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_user_by_id(anyio_backend, ac: AsyncClient, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await ac.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_user_by_id_error_not_found(anyio_backend, ac: AsyncClient):
    response = await ac.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_update_user(anyio_backend, ac: AsyncClient, user):
    response = await ac.put(
        '/users/1',
        json={
            'username': 'test2',
            'email': 'test2@example.com',
            'password': 'thisismypassword',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'test2',
        'email': 'test2@example.com',
        'id': 1,
    }


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_update_user_error_not_found(anyio_backend, ac: AsyncClient):
    response = await ac.put(
        '/users/999',
        json={
            'username': 'test2',
            'email': 'test2@example.com',
            'password': 'thisismypassword',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_delete_user(anyio_backend, ac: AsyncClient, user):
    response = await ac.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_delete_user_error_not_found(anyio_backend, ac: AsyncClient):
    response = await ac.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
