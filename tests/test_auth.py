from http import HTTPStatus

import pytest
from freezegun import freeze_time
from httpx import AsyncClient


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_get_token(anyio_backend, ac: AsyncClient, user):
    response = await ac.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_token_wrong_password(anyio_backend, ac: AsyncClient, user):
    response = await ac.post(
        '/auth/token',
        data={'username': user.username, 'password': 'anypassword'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_token_wrong_username(anyio_backend, ac: AsyncClient, user):
    response = await ac.post(
        '/auth/token',
        data={'username': 'anyusername', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_token_expired_after_time(anyio_backend, ac: AsyncClient, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = await ac.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = await ac.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_refresh_token(anyio_backend, ac: AsyncClient, token):
    response = await ac.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_token_expired_dont_refresh(
    anyio_backend, ac: AsyncClient, user
):
    with freeze_time('2023-07-14 12:00:00'):
        response = await ac.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = await ac.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
