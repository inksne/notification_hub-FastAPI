from fastapi import APIRouter
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

import logging

from .exceptions import internal_server_error, telegram_forbidden_error, telegram_retry_after_error
from ..config import configure_logging
from ..basemodels import TelegramHandlerModel
from ..database.database import get_async_session
from ..database.managers import db_manager
from ..bot.bot import bot
from ..bot.texts import generate_notify_text



router = APIRouter(tags=['Telegram Handler'], prefix='/api/v1')


configure_logging()
logger = logging.getLogger(__name__)



'''
Входящий json:
{
  "messages": {
    "telegram": '...',
    "email": '...',
  },
  "channels": ["telegram", "email"],
  "targets": {
    'telegram': '123456789,
    'email': 'email@example.com'
  }
}
'''



@router.post('/telegram')
async def handle_telegram_notify(data: TelegramHandlerModel) -> None:
    try:
        async for session in get_async_session():
            chat_id = await db_manager.get_chat_id(username=data.username, session=session)

        await bot.send_message(chat_id=chat_id, text=generate_notify_text(data.message))

    except TelegramForbiddenError as e:
        logger.error('TelegramForbiddenError', e)

        async for session in get_async_session():
            await db_manager.delete_chat_id(username=data.username, session=session)

        raise telegram_forbidden_error

    except TelegramRetryAfter as e:
        logger.error('TelegramRetryAfterError', e)
        raise telegram_retry_after_error

    except Exception as e:
        logger.error(e)
        raise internal_server_error