from http import HTTPStatus

import pytest
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
async def test_get_token_error_unauthorized(anyio_backend, ac: AsyncClient):
    response = await ac.post(
        '/auth/token',
        data={'username': 'dont_exists', 'password': 'anypassword'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}
