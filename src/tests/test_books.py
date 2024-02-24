from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Book, Seller


async def test_create_book(
    async_client: AsyncClient,
    test_seller: Seller,
    jwt_token: str,
):
    book = {
        'title': 'Agile Principles Revisited',
        'author': 'Robert Martin',
        'year': 2024,
        'pages': 350,
    }
    response = await async_client.post(
        url='/api/v1/books/',
        json=book,
        headers={
            'Authorization': f'Bearer {jwt_token}',
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    res = response.json()
    assert 'id' in res
    assert res['title'] == 'Agile Principles Revisited'
    assert res['author'] == 'Robert Martin'
    assert res['year'] == 2024
    assert res['count_pages'] == 350
    assert res['seller_id'] == test_seller.id


async def test_get_all_books(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_book: Book,
    test_seller: Seller,
):
    test_book_2 = Book(title='1984', author='George Orwell', year=1949, count_pages=328, seller_id=test_seller.id)
    db_session.add(test_book_2)
    await db_session.flush()

    response = await async_client.get('/api/v1/books/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['books']) == 2

    assert response.json() == {
        'books': [
            {
                'id': test_book.id,
                'title': 'Hogwarts',
                'author': 'J.K. Rowling',
                'year': 2024,
                'count_pages': 450,
                'seller_id': test_seller.id,
            },
            {
                'id': test_book_2.id,
                'title': '1984',
                'author': 'George Orwell',
                'year': 1949,
                'count_pages': 328,
                'seller_id': test_seller.id,
            },
        ]
    }


async def test_get_single_book(
    async_client: AsyncClient,
    test_book: Book,
    test_seller: Seller,
):
    response = await async_client.get(f'/api/v1/books/{test_book.id}')
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        'id': test_book.id,
        'title': 'Hogwarts',
        'author': 'J.K. Rowling',
        'year': 2024,
        'count_pages': 450,
        'seller_id': test_seller.id,
    }


async def test_delete_book(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_book: Book,
):
    response = await async_client.delete(f'/api/v1/books/{test_book.id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(Book))
    db_result = all_books.scalars().all()
    assert len(db_result) == 0


async def test_update_book(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_book: Book,
    jwt_token: str,
):
    response = await async_client.put(
        url=f'/api/v1/books/{test_book.id}',
        json={'title': '1984', 'author': 'George Orwell', 'year': 1949, 'pages': 328},
        headers={'Authorization': f'Bearer {jwt_token}'},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    await db_session.flush()

    book = await db_session.get(Book, test_book.id)
    assert book.title == '1984'
    assert book.author == 'George Orwell'
    assert book.year == 1949
    assert book.count_pages == 328
