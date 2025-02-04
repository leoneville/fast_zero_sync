from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time


def test_get_token(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_token_wrong_password(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'anypassword'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_token_wrong_username(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': 'anyusername', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_token_expired_after_time(client: TestClient, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.put(
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


def test_refresh_token(client: TestClient, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_token_expired_dont_refresh(client: TestClient, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
