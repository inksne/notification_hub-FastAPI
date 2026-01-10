from fastapi import APIRouter
from starlette import status

import logging

from .telegram_handler import handle_telegram_notify
from .email_handler import handle_email_notify
from .exceptions import internal_server_error
from ..config import configure_logging
from ..basemodels import ChannelsHandlerModel, TelegramHandlerModel, EmailRequestModel



router = APIRouter(tags=['Channels Handler'], prefix='/api/v1')


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
    'telegram': '123456789',
    'email': 'email@example.com'
  }
}
'''



@router.post('/channels', status_code=status.HTTP_204_NO_CONTENT)
async def handle_channels(data: ChannelsHandlerModel) -> None:
    try:
        # try:
        #     async with httpx.AsyncClient() as client:
        #         if 'telegram' in data.targets:
        #             request_data = TelegramHandlerModel(
        #                 message=data.messages['telegram'],
        #                 username=data.targets['telegram'],
        #             )

        #             await client.post(
        #                 url=f'{APP_HOST}/api/v1/telegram',
        #                 json=request_data.model_dump(),
        #             )

        # except (httpx.HTTPStatusError, httpx.RequestError) as e:
        #     logger.error(e)
        #     raise internal_server_error


        if 'telegram' in data.targets:
            telegram_username = data.targets['telegram']

            if telegram_username.startswith('@'):
                telegram_username = telegram_username[1:]

            request_data = TelegramHandlerModel(
                message=data.messages['telegram'],
                username=telegram_username
            )

            await handle_telegram_notify(request_data)

        if 'email' in data.targets:
            request_data = EmailRequestModel(
                body=data.messages['email'],
                to_email=data.targets['email']
            )

            await handle_email_notify(request_data)

    except Exception as e:
        logger.error(e)
        raise internal_server_error