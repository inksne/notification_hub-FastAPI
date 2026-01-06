from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.chat_action import ChatAction

import logging

from .texts import generate_start_text, generate_help_text, internal_error_text
from ..config import configure_logging



router = Router(name=__name__)


configure_logging()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def handle_start(msg: types.Message) -> None:
    try:
        await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)

        await msg.answer(generate_start_text(msg), ParseMode.HTML)

    except Exception as e:
        logger.error(e)
        await msg.answer(internal_error_text)


@router.message(Command('help'))
async def handle_help(msg: types.Message) -> None:
    try:
        await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)

        await msg.answer(generate_help_text(), ParseMode.HTML)

    except Exception as e:
        logger.error(e)
        await msg.answer(internal_error_text)