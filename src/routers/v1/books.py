from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select

from src.models import Book, Seller
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBookWithSellerId
from src.tools import DBSession, get_current_seller

books_router = APIRouter(tags=['books'], prefix='/books')


@books_router.post(path='/', response_model=ReturnedBookWithSellerId, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: IncomingBook,
    session: DBSession,
    current_seller: Annotated[Seller, Depends(get_current_seller)],
):
    new_book = Book(
        title=book.title,
        author=book.author,
        year=book.year,
        count_pages=book.count_pages,
        seller_id=current_seller.id,
    )
    session.add(new_book)
    await session.flush()

    return new_book


@books_router.get(path='/', response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    query = select(Book)
    db_result = await session.execute(query)
    books = db_result.scalars().all()
    return {'books': books}


@books_router.get(path='/{book_id}', response_model=ReturnedBookWithSellerId)
async def get_book(book_id: int, session: DBSession):
    if book := await session.get(Book, book_id):
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.delete(path='/{book_id}')
async def delete_book(book_id: int, session: DBSession):
    if deleted_book := await session.get(Book, book_id):
        await session.delete(deleted_book)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.put(path='/{book_id}', response_model=ReturnedBookWithSellerId, status_code=status.HTTP_202_ACCEPTED)
async def update_book(
    book_id: int,
    new_data: IncomingBook,
    session: DBSession,
    _: Annotated[Seller, Depends(get_current_seller)],  # здесь происходит авторизация
):
    if updated_book := await session.get(Book, book_id):
        updated_book.author = new_data.author
        updated_book.title = new_data.title
        updated_book.year = new_data.year
        updated_book.count_pages = new_data.count_pages

        await session.flush()
        return updated_book

    return Response(status_code=status.HTTP_404_NOT_FOUND)
