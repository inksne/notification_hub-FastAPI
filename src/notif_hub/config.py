from pydantic_settings import BaseSettings, SettingsConfigDict

import os
import logging
from typing import Final



class ConstantSettings(BaseSettings):
    POSTGRES_USER: Final[str]
    POSTGRES_PASSWORD: Final[str]
    POSTGRES_DB: Final[str]
    POSTGRES_HOST: Final[str]

    TELEGRAM_API_KEY: Final[str]

    OAUTH_GOOGLE_CLIENT_SECRET: Final[str]
    OAUTH_GOOGLE_CLIENT_ID: Final[str]

    REDIRECT_URI: Final[str] = "http://localhost:8000/authenticated"
    GOOGLE_TOKEN_URL: Final[str] = "https://oauth2.googleapis.com/token"

    GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
    GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")

    EMAIL_SENDER_ADDRESS: Final[str]
    EMAIL_PASSWORD: Final[str]
    EMAIL_SUBJECT: Final[str] = '🔔 Сообщение с Notification Hub'
    EMAIL_HOST: Final[str] = "smtp.yandex.ru"
    EMAIL_PORT: Final[int] = 465

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
        env_file_encoding='utf-8'
    )

constant_settings = ConstantSettings()


class DBSettings(BaseSettings):
    db_url: str = f'postgresql+asyncpg://{constant_settings.POSTGRES_USER}:{constant_settings.POSTGRES_PASSWORD}@{constant_settings.POSTGRES_HOST}:5432/{constant_settings.POSTGRES_DB}'

db_settings = DBSettings()


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
    )