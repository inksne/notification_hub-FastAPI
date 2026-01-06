from aiogram import Bot, Dispatcher

from ..config import TELEGRAM_API_KEY



bot = Bot(token=TELEGRAM_API_KEY)
dp = Dispatcher()