from http import HTTPStatus

from fastapi.testclient import TestClient


def test_read_root_deve_retornar_ok_e_ola_mundo(client: TestClient):
    response = client.get('/')  # Act (ação)

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Olá Mundo!'}  # assert
