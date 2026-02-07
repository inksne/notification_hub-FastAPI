from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

import os
import logging
from typing import Final
from pathlib import Path



class ConstantSettings(BaseSettings):
    POSTGRES_USER: Final[str]
    POSTGRES_PASSWORD: Final[str]
    POSTGRES_DB: Final[str]
    POSTGRES_HOST: Final[str]

    REDIS_HOST: Final[str]
    REDIS_STATE_PREFIX: str = "oauth:state:"
    REDIS_STATE_TTL: int = 900

    TELEGRAM_API_KEY: Final[str]

    OAUTH_GOOGLE_CLIENT_SECRET: Final[str]
    OAUTH_GOOGLE_CLIENT_ID: Final[str]

    REDIRECT_URI: str = "http://localhost:8000/authenticated"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"

    GOOGLE_JWKS_URI: str = "https://www.googleapis.com/oauth2/v3/certs"
    GOOGLE_ISSUERS: tuple = ("https://accounts.google.com", "accounts.google.com")

    OAUTH_GITHUB_CLIENT_ID: Final[str]
    OAUTH_GITHUB_CLIENT_SECRET: Final[str]

    GITHUB_AUTH_URL: str = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    GITHUB_ACCESS_URL: str = "https://api.github.com/user"

    EMAIL_SENDER_ADDRESS: Final[str]
    EMAIL_PASSWORD: Final[str]
    EMAIL_SUBJECT: str = "🔔 Сообщение с Notification Hub"
    EMAIL_HOST: str = "smtp.yandex.ru"
    EMAIL_PORT: int = 465

    TOKEN_TYPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"

    PATH_TO_SERVER_CRT: str = "/app/src/notif_hub/certs/server.crt"
    PATH_TO_SERVER_KEY: str = "/app/src/notif_hub/certs/server.key"

    UVICORN_APP: str = "src.notif_hub.main:app"
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    APP_TITLE: str = "Notification Hub"
    APP_VERSION: str = "0.1.19"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
        env_file_encoding='utf-8'
    )

constant_settings = ConstantSettings()


class DBSettings(BaseSettings):
    db_url: str = f'postgresql+asyncpg://{constant_settings.POSTGRES_USER}:{constant_settings.POSTGRES_PASSWORD}@{constant_settings.POSTGRES_HOST}:5432/{constant_settings.POSTGRES_DB}'

db_settings = DBSettings()


class AuthJWT(BaseModel):
    private_key_path: Path = Path("src/notif_hub/certs") / "jwt-private.pem"
    public_key_path: Path = Path("src/notif_hub/certs") / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 3
    refresh_token_expire_days: int = 30


class AuthSettings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


auth_settings = AuthSettings()


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
    )