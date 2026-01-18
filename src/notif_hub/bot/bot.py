from aiogram import Bot, Dispatcher

from ..config import constant_settings



bot = Bot(token=constant_settings.TELEGRAM_API_KEY)
dp = Dispatcher()