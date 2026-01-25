from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import logging
import asyncio
import uvicorn

from .database.database import create_db_and_tables
from .templates import templates_router
from .bot import bot, dp, commands_router
from .api import channels_router, telegram_router, email_router, webhook_router
from .auth import google_auth_router, github_auth_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title='Notification Hub', lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(templates_router)
app.include_router(channels_router)
app.include_router(telegram_router)
app.include_router(email_router)
app.include_router(webhook_router)
app.include_router(google_auth_router)
app.include_router(github_auth_router)



async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


async def main():
    dp.include_router(commands_router)
    uvicorn_config = uvicorn.Config("src.notif_hub.main:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(uvicorn_config)

    await asyncio.gather(start_bot(), server.serve())


if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        exit(0)