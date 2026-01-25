from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.chat_action import ChatAction

import logging

from .texts import generate_start_text, generate_help_text, internal_error_text
from ..config import configure_logging
from ..database.database import get_async_session
from ..database.managers import psql_manager



router = Router(name=__name__)


configure_logging()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def handle_start(msg: types.Message) -> None:
    try:
        if not msg.bot or not msg.from_user:    # mypy
            return

        await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)

        async for session in get_async_session():
            if not await psql_manager.get_chat_id(username=msg.from_user.username, session=session):
                await psql_manager.add_chat_id(chat_id=msg.chat.id, username=msg.from_user.username, session=session)

        await msg.answer(text=generate_start_text(msg), parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(e)
        await msg.answer(internal_error_text)


@router.message(Command('help'))
async def handle_help(msg: types.Message) -> None:
    try:
        if not msg.bot or not msg.from_user:    # mypy
            return

        await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)

        async for session in get_async_session():
            if not await psql_manager.get_chat_id(username=msg.from_user.username, session=session):
                await psql_manager.add_chat_id(chat_id=msg.chat.id, username=msg.from_user.username, session=session)

        await msg.answer(text=generate_help_text(), parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(e)
        await msg.answer(internal_error_text)