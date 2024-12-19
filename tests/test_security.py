from http import HTTPStatus

import pytest
from httpx import AsyncClient
from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)

    result = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert result['sub'] == data['sub']
    assert result['exp']


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_jwt_invalid_token(anyio_backend, ac: AsyncClient):
    response = await ac.delete(
        '/users/', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
