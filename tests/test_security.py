from http import HTTPStatus

import pytest
from httpx import AsyncClient
from jwt import decode

from fast_zero.security import create_access_token, settings


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)

    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_jwt_invalid_token(anyio_backend, ac: AsyncClient, user):
    response = await ac.delete(
        f'/users/{user.id}', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_get_current_user_not_found(anyio_backend, ac: AsyncClient):
    data = {'no-username': 'nonuser'}
    token = create_access_token(data)

    response = await ac.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_get_current_user_does_not_exists(
    anyio_backend, ac: AsyncClient
):
    data = {'sub': 'nonuser'}
    token = create_access_token(data)

    response = await ac.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
