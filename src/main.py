from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.configurations import create_db_and_tables, delete_db_and_tables, global_init
from src.routers import v1_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Запускается при старте приложения.
    global_init()
    await create_db_and_tables()
    yield
    # Запускается при остановке приложения.
    await delete_db_and_tables()


# Само приложение FastAPI. Именно оно запускается сервером и служит точкой входа.
# В нем можно указать разные параметры для Swagger и для ручек (endpoints).
def create_application():
    return FastAPI(
        title='Book Library App',
        description='FastAPI приложение для МТС ШАД',
        version='0.1.0',
        responses={404: {'description': 'Not Found!'}},
        default_response_class=ORJSONResponse,  # Подключаем быстрый serializer.
        lifespan=lifespan,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},  # Скрываем раздел Schema в Docs
    )


app = create_application()


def _configure():
    app.include_router(v1_router)


_configure()
