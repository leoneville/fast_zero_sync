from http import HTTPStatus

from fastapi.testclient import TestClient
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


def test_jwt_invalid_token(client: TestClient, user):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_not_found(client: TestClient):
    data = {'no-username': 'nonuser'}
    token = create_access_token(data)

    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_does_not_exists(client: TestClient):
    data = {'sub': 'nonuser'}
    token = create_access_token(data)

    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
