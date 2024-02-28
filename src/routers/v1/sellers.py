from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.models import Seller
from src.schemas import BaseSeller, IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerWithBooks
from src.tools import DBSession, get_current_seller, hash_password

seller_router = APIRouter(tags=['seller'], prefix='/seller')


@seller_router.post(path='/', response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        hashed_password=hash_password(seller.password),
    )
    session.add(new_seller)
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists')

    return new_seller


@seller_router.get(path='/', response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    db_result = await session.execute(query)
    sellers = db_result.scalars().all()
    return {'sellers': sellers}


@seller_router.get(path='/{seller_id}', response_model=ReturnedSellerWithBooks)
async def get_seller(
    seller_id: int,
    session: DBSession,
    _: Annotated[Seller, Depends(get_current_seller)],  # здесь происходит авторизация
):
    query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    db_result = await session.execute(query)

    if seller := db_result.scalars().first():
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@seller_router.delete(path='/{seller_id}')
async def delete_seller(seller_id: int, session: DBSession):
    if deleted_seller := await session.get(Seller, seller_id):
        await session.delete(deleted_seller)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@seller_router.put(path='/{seller_id}', response_model=ReturnedSeller, status_code=status.HTTP_202_ACCEPTED)
async def update_seller(seller_id: int, new_data: BaseSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()
        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
