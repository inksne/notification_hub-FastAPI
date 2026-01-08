from dotenv import load_dotenv
from pydantic_settings import BaseSettings

import os
import logging
from typing import Final



load_dotenv()


POSTGRES_USER: Final[str] = os.environ.get("POSTGRES_USER", "inksne")
POSTGRES_PASSWORD: Final[str] = os.environ.get("POSTGRES_PASSWORD", "inksne")
POSTGRES_DB: Final[str] = os.environ.get("POSTGRES_DB", "inksne")
POSTGRES_HOST: Final[str] = os.environ.get("POSTGRES_HOST", "postgres")

TELEGRAM_API_KEY: Final[str] = os.environ.get("TELEGRAM_API_KEY", "null")
EMAIL_API_KEY: Final[str] = os.environ.get("EMAIL_API_KEY", "null")


class DBSettings(BaseSettings):
    db_url: str = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'

db_settings = DBSettings()


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
    )