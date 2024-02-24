from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Book(BaseModel):
    __tablename__: str = 'books_table'  # noqa

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer)
    count_pages: Mapped[int] = mapped_column(Integer)
    seller_id: Mapped[int] = mapped_column(ForeignKey('sellers_table.id'), nullable=False)
    seller = relationship(argument='Seller', back_populates='books', single_parent=True)
