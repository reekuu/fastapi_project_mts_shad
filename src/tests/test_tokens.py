import re

from httpx import AsyncClient
from starlette import status

from src.models import Seller


async def test_login_for_access_token(
    async_client: AsyncClient,
    test_seller: Seller,
):
    response = await async_client.post(
        url='api/v1/token/',
        data={
            'username': test_seller.email,
            'password': '(X8r8ez@nw',
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    token_raw = response.json()
    assert 'token_type' in token_raw
    assert token_raw['token_type'] == 'bearer'
    assert 'access_token' in token_raw
    pattern = re.compile(r'^(.+)\.(.+)\.(.+)$')
    assert pattern.search(token_raw['access_token'])


async def test_login_with_wrong_password(
    async_client: AsyncClient,
    test_seller: Seller,
):
    response = await async_client.post(
        url='api/v1/token/',
        data={
            'username': test_seller.email,
            'password': 'wrong_password',
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
