from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ['IncomingBook', 'ReturnedBookWithSellerId', 'ReturnedBook', 'ReturnedAllBooks']


class BaseBook(BaseModel):
    title: str
    author: str
    year: int


class BookID(BaseModel):
    id: int


class IncomingBook(BaseBook):
    year: int
    count_pages: int = Field(alias='pages')

    @field_validator('title', 'author')  # noqa
    @staticmethod
    def validate_field_length(val: str):
        if len(val) > 100:
            raise PydanticCustomError('Validation error', 'Value is to long!')
        return val

    @field_validator('year')  # noqa
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise PydanticCustomError('Validation error', 'Year is wrong!')
        return val


class ReturnedBook(BaseBook, BookID):
    id: int
    count_pages: int


class ReturnedBookWithSellerId(ReturnedBook, BookID):
    seller_id: int


class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBookWithSellerId]
