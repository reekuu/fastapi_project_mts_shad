"""
Это модуль с фикстурами для PyTest.
Фикстуры — это специальные функции, которые не требуют явного импорта.
PyTest автоматически обнаруживает их по имени из файла conftest.py.
"""

import asyncio

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.configurations.settings import settings
from src.models import BaseModel, Book, Seller
from src.tools import generate_token, hash_password

# Переопределяем движок для запуска тестов и подключаем его к тестовой базе.
# Это решает проблему с сохранностью данных в основной базе приложения. Фикстуры тестов их не зачистят.
# Также обеспечивает чистую среду для запуска тестов. В ней не будет лишних записей.
async_test_engine = create_async_engine(
    settings.database_test_url,
    echo=True,
)

# Создаем фабрику сессий для тестового движка.
async_test_session = async_sessionmaker(async_test_engine, expire_on_commit=False, autoflush=False)


# Получаем цикл событий для асинхронного потока выполнения задач.
@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    # loop = asyncio.new_event_loop() # На разных версиях питона и разных ОС срабатывает по-разному.
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# Создаем таблицы в тестовой БД. Предварительно удаляя старые.
@pytest.fixture(scope='session', autouse=True)
async def create_tables() -> None:
    """Create tables in DB."""
    async with async_test_engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.drop_all)
        await connection.run_sync(BaseModel.metadata.create_all)


# Создаем сессию для БД используемую для тестов.
@pytest.fixture
async def db_session():
    async with async_test_engine.connect() as connection:
        async with async_test_session(bind=connection) as session:
            yield session
            await session.rollback()


# Мы не можем создать 2 приложения (app) - это приведет к ошибкам.
# Поэтому, на время запуска тестов мы подменяем там зависимость с сессией.
@pytest.fixture
def test_app(db_session):
    from src.configurations.database import get_async_session
    from src.main import app

    app.dependency_overrides[get_async_session] = lambda: db_session

    return app


# Создаем асинхронного клиента для ручек.
@pytest.fixture
async def async_client(test_app):
    async with httpx.AsyncClient(app=test_app, base_url='http://127.0.0.1:8000') as test_client:
        yield test_client


@pytest.fixture
async def test_seller(db_session: AsyncSession):
    seller = Seller(
        first_name='Serena',
        last_name='Williams',
        email='loud@rocket.com',
        hashed_password=hash_password('(X8r8ez@nw'),
    )
    db_session.add(seller)
    await db_session.flush()

    return seller


@pytest.fixture
async def test_book(db_session: AsyncSession, test_seller: Seller):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку, которая может случиться в POST ручке.
    book = Book(
        title='Hogwarts',
        author='J.K. Rowling',
        year=2024,
        count_pages=450,
        seller_id=test_seller.id,
    )
    db_session.add(book)
    await db_session.flush()

    return book


@pytest.fixture
def jwt_token(test_seller: Seller) -> str:
    return generate_token(claims={'sub': test_seller.email})
