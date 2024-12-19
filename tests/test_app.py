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
async def test_create_user_error_username_conflict(
    anyio_backend, ac: AsyncClient, user
):
    payload = {
        'username': 'Teste',
        'email': 'neville@example.com',
        'password': 'thisismypassword',
    }
    response = await ac.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_create_user_error_email_conflict(
    anyio_backend, ac: AsyncClient, user
):
    payload = {
        'username': 'neville',
        'email': 'teste@test.com',
        'password': 'thisismypassword',
    }
    response = await ac.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_users_with_user(
    anyio_backend, ac: AsyncClient, user, token
):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await ac.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_user_by_id(anyio_backend, ac: AsyncClient, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await ac.get(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_user_by_id_error_not_found(
    anyio_backend, ac: AsyncClient, token
):
    response = await ac.get(
        '/users/999', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_update_user(anyio_backend, ac: AsyncClient, user, token):
    response = await ac.put(
        '/users/',
        json={
            'username': 'test2',
            'email': 'test2@example.com',
            'password': 'thisismypassword',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'test2',
        'email': 'test2@example.com',
        'id': user.id,
    }


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_delete_user(anyio_backend, ac: AsyncClient, token):
    response = await ac.delete(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_get_token(anyio_backend, ac: AsyncClient, user):
    response = await ac.post(
        '/token',
        data={'username': user.username, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_get_token_error_unauthorized(anyio_backend, ac: AsyncClient):
    response = await ac.post(
        '/token',
        data={'username': 'dont_exists', 'password': 'anypassword'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}
