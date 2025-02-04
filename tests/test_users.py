from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.schemas import UserPublic


def test_create_user(client: TestClient):
    payload = {
        'username': 'neville',
        'email': 'neville@example.com',
        'password': 'thisismypassword',
    }

    response = client.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'neville',
        'email': 'neville@example.com',
    }


def test_create_user_error_username_conflict(client: TestClient, user):
    payload = {
        'username': user.username,
        'email': 'neville@example.com',
        'password': 'thisismypassword',
    }
    response = client.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_error_email_conflict(client: TestClient, user):
    payload = {
        'username': 'neville',
        'email': user.email,
        'password': 'thisismypassword',
    }
    response = client.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users_with_user(client: TestClient, user, token, other_user):
    user_schema = UserPublic.model_validate(user).model_dump()
    other_user_schema = UserPublic.model_validate(other_user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema, other_user_schema]}


def test_read_user_by_id(client: TestClient, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_by_id_error_not_found(client: TestClient, token):
    response = client.get(
        '/users/999', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client: TestClient, user, token):
    response = client.put(
        f'/users/{user.id}',
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


def test_update_user_error_username_conflict(
    client: TestClient, user, other_user, token
):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': other_user.username,
            'email': user.email,
            'password': 'thisismypassword',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_update_user_error_email_conflict(
    client: TestClient, user, other_user, token
):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': user.username,
            'email': other_user.email,
            'password': 'thisismypassword',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_update_user_with_wrong_user(client: TestClient, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client: TestClient, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_with_wrong_user(client: TestClient, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
