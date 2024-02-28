from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from src.models import Seller
from src.schemas import Token
from src.tools import DBSession, UnauthorizedException, generate_token, verify_password

token_router = APIRouter(tags=['token'], prefix='/token')


@token_router.post(path='/', response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_jwt_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DBSession,
):
    query = select(Seller).where(Seller.email == form_data.username)
    db_result = await session.execute(query)
    seller = db_result.scalar_one_or_none()

    if not seller or not verify_password(form_data.password, seller.hashed_password):
        raise UnauthorizedException('Incorrect email or password')

    access_token = generate_token(claims={'sub': seller.email})
    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }
