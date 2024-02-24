import re

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

from .books import ReturnedBook

__all__ = ['IncomingSeller', 'ReturnedSeller', 'ReturnedSellerWithBooks', 'ReturnedAllSellers', 'BaseSeller']


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

    @staticmethod
    @field_validator('first_name', 'last_name')
    def validate_field_length(val: str) -> str:
        if len(val) > 50:
            raise PydanticCustomError('Validation error', 'Value is to long!')
        return val


class SellerID(BaseModel):
    id: int = 1


class IncomingSeller(BaseSeller):
    password: str = Field(
        default='pass-aA8',
        description='\n'.join(
            [
                'Пароль должен соответствовать следующим критериям:',
                '* Содержать строчные буквы;',
                '* Содержать заглавные буквы;',
                '* Содержать хотя бы одну цифру;',
                '* Иметь длину не менее 8 символов;',
            ]
        ),
    )

    @staticmethod
    @field_validator('password')
    def validate_password(password: str) -> str:
        """Проверка на сложность пароля."""
        pattern = re.compile(r'^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?\d)\S{8,}$')
        if not pattern.search(password):
            raise PydanticCustomError('Validation error', 'Password is too simple!')
        return password


class ReturnedSeller(BaseSeller, SellerID):
    pass


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook]


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
