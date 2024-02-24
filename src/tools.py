from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # noqa: python-jose in fact
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.configurations import get_async_session
from src.configurations.settings import settings
from src.models import Seller

ACCESS_TOKEN_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/token/')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = 'Incorrect JWT token'):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={'WWW-Authenticate': 'Bearer'},
        )


def hash_password(password: str) -> str:
    """Возвращает хэшированный пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с его хэшированной версией."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(claims: dict, expires_delta: Optional[timedelta] = None):
    """Возвращает сгенерированный jwt токен."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta

    claims.update({'exp': expire})
    return jwt.encode(
        claims=claims,
        key=settings.jwt_secret_key,
        algorithm=ACCESS_TOKEN_ALGORITHM,
    )


def get_email_from_token(access_token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """Возвращает email из токена."""
    try:
        payload = jwt.decode(
            token=access_token,
            key=settings.jwt_secret_key,
            algorithms=[ACCESS_TOKEN_ALGORITHM],
        )
    except JWTError:
        raise UnauthorizedException()

    seller_email = payload.get('sub')
    if not seller_email:
        raise UnauthorizedException()

    return seller_email


async def get_current_seller(
    db_session: DBSession,
    seller_email: Annotated[str, Depends(get_email_from_token)],
) -> Seller:
    """Возвращает продавца из токена."""
    stmt = select(Seller).where(Seller.email == seller_email)
    db_result = await db_session.execute(stmt)
    seller = db_result.scalar_one_or_none()
    if not seller:
        raise UnauthorizedException()

    return seller
