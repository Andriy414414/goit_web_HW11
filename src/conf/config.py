from typing import Any

from pydantic import ConfigDict, field_validator

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = 'postgresql+asyncpg://postgres:111111@localhost:1111/ghf'
    SECRET_KEY_JWT: str = 'dsdsfgsdfg'
    ALGORITHM: str = 'HS256'
    MAIL_USERNAME: str = 'fghdf@meta.ua'
    MAIL_PASSWORD: str = 'dfgdfgs'
    MAIL_FROM: str = 'fghdf@meta.ua'
    MAIL_PORT: int = 465
    MAIL_SERVER: str = 'smtp.meta.ua'
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None
    CLD_NAME: str = "abc"
    CLD_API_KEY: int = 37249843695273
    CLD_API_SECRET: str = "secret"

    @field_validator('ALGORITHM')
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ['HS256', 'HS512']:
            raise ValueError('Algorithm must be HS256 or HS512')
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8") # noqa


config = Settings()
