"""
Модуль с настройками окружения.
Служит для того, чтобы все настройки были сосредоточены в одном месте.
А также для возможности подтягивания переменных из окружения (секретов).

Для того чтобы переменные были импортированы, необходимо создать файл .env и поместить в него переменные,
определённые в настройках (db_host, db_name, jwt_secret_key). Пример находится в файле .env.example.

Важно! Файл .env не должен попадать в git commit.
Он содержит информацию о том, как подключаться к базе данных (БД) и другие секреты,
что может позволить злоумышленникам получить доступ к приложению.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_test_name: str = 'fastapi_project_test_db'
    max_connection_count: int = 10
    jwt_secret_key: str = 'jwt_secret_key'

    @property
    def database_url(self) -> str:
        return f'{self.db_host}/{self.db_name}'

    @property
    def database_test_url(self) -> str:
        return f'{self.db_host}/{self.db_test_name}'

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
