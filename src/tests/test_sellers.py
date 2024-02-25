from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Book, Seller
from src.tools import hash_password


async def test_create_seller(async_client: AsyncClient):
    seller = {
        'first_name': 'Serena',
        'last_name': 'Williams',
        'email': 'loud@rocket.com',
        'password': '(X8r8ez@nw',
    }
    response = await async_client.post(url='/api/v1/seller/', json=seller)
    assert response.status_code == status.HTTP_201_CREATED

    res = response.json()
    assert res['first_name'] == 'Serena'
    assert res['last_name'] == 'Williams'
    assert res['email'] == 'loud@rocket.com'


async def test_create_duplicate_seller(async_client: AsyncClient, test_seller: Seller):
    seller = {
        'first_name': 'Serena',
        'last_name': 'Williams',
        'email': test_seller.email,
        'password': '(X8r8ez@nw',
    }
    response = await async_client.post(url='/api/v1/seller/', json=seller)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json() == {
        'detail': 'Email already exists',
    }


async def test_get_all_sellers(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_seller: Seller,
):
    test_seller_2 = Seller(
        first_name='Ivan', last_name='Godunov', email='ivan@mail.ru', hashed_password=hash_password('qwerty123')
    )
    db_session.add(test_seller_2)
    await db_session.flush()

    response = await async_client.get('/api/v1/seller/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['sellers']) == 2
    assert response.json() == {
        'sellers': [
            {
                'id': test_seller.id,
                'first_name': 'Serena',
                'last_name': 'Williams',
                'email': 'loud@rocket.com',
            },
            {
                'id': test_seller_2.id,
                'first_name': 'Ivan',
                'last_name': 'Godunov',
                'email': 'ivan@mail.ru',
            },
        ]
    }


async def test_get_single_seller(
    async_client: AsyncClient,
    test_seller: Seller,
    test_book: Book,
    jwt_token: str,
):
    response = await async_client.get(
        url=f'/api/v1/seller/{test_seller.id}',
        headers={'Authorization': f'Bearer {jwt_token}'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': test_seller.id,
        'first_name': 'Serena',
        'last_name': 'Williams',
        'email': 'loud@rocket.com',
        'books': [
            {
                'id': test_book.id,
                'title': 'Hogwarts',
                'author': 'J.K. Rowling',
                'year': 2024,
                'count_pages': 450,
            },
        ],
    }


async def test_get_nonexistent_seller(
    async_client: AsyncClient,
    test_seller: Seller,
    jwt_token: str,
):
    response = await async_client.get(
        url='/api/v1/seller/-1',
        headers={'Authorization': f'Bearer {jwt_token}'},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_seller(
    db_session: AsyncSession,
    async_client: AsyncClient,
    test_seller: Seller,
):
    response = await async_client.delete(f'/api/v1/seller/{test_seller.id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


async def test_update_seller(
    db_session: AsyncSession,
    async_client: AsyncClient,
    test_seller: Seller,
):
    response = await async_client.put(
        url=f'/api/v1/seller/{test_seller.id}',
        json={'first_name': 'Hannah', 'last_name': 'Miller', 'email': 'joshuaward@gmail.com'},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    await db_session.flush()

    updated_seller = await db_session.get(Seller, test_seller.id)
    assert updated_seller.id == test_seller.id
    assert updated_seller.first_name == 'Hannah'
    assert updated_seller.last_name == 'Miller'
    assert updated_seller.email == 'joshuaward@gmail.com'
