from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_read_root_deve_retornar_ok_e_ola_mundo(
    anyio_backend, ac: AsyncClient
):
    response = await ac.get('/')  # Act (ação)

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Olá Mundo!'}  # assert
