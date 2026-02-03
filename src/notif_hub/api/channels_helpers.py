from starlette import status

import httpx
import logging
from typing import Union

from ..config import configure_logging
from ..basemodels import (
    ChannelsHandlerModel,
    TelegramHandlerModel,
    EmailRequestModel,
    WebhookRequestModel
)
from .telegram_handler import handle_telegram_notify
from .email_handler import handle_email_notify
from .webhook_handler import handle_webhook_notify
from .exceptions import (
    webhook_bad_request_error,
    webhook_unauthorized_error,
    webhook_forbidden_error,
    webhook_not_found_error,
    webhook_method_not_allowed_error,
    webhook_too_many_requests_error,
    webhook_unavailable_for_legal_reasons_error,
    internal_server_error
)


configure_logging()
logger = logging.getLogger(__name__)



async def process_channels(data: ChannelsHandlerModel) -> Union[str, list[str]]:
    data_notification_message: str = ''
    recipient: list[str] = []

    if 'telegram' in data.targets:
        telegram_target = data.targets['telegram']

        if not isinstance(telegram_target, str):
            raise ValueError("mypy")

        telegram_username = telegram_target

        if telegram_username.startswith('@'):
            telegram_username = telegram_username[1:]

        data_telegram_message = data.messages['telegram']

        telegram_request = TelegramHandlerModel(
            message=data_telegram_message,
            username=telegram_username
        )

        await handle_telegram_notify(telegram_request)

        data_notification_message = data_telegram_message
        recipient.append(telegram_target)

    if 'email' in data.targets:
        email_target = data.targets['email']

        if not isinstance(email_target, str):
            raise ValueError("mypy")

        data_email_message = data.messages['email']

        email_request = EmailRequestModel(
            body=data_email_message,
            to_email=email_target
        )

        await handle_email_notify(email_request)

        data_notification_message = data_email_message
        recipient.append(email_target)

    if 'webhook' in data.targets:
        webhook_target = data.targets['webhook']

        if not isinstance(webhook_target, dict):
            raise ValueError("mypy")

        data_webhook_message = data.messages['webhook']

        webhook_request = WebhookRequestModel(
            message=data_webhook_message,
            url=webhook_target['url'],
            format=webhook_target['format'],
            param_name=webhook_target['param_name']
        )

        await handle_webhook_notify(webhook_request)

        data_notification_message = data_webhook_message
        recipient.append(webhook_target)

    return data_notification_message, recipient


def handle_http_status_errors(e: httpx.HTTPStatusError) -> None:
    status_code = e.response.status_code

    if status_code == status.HTTP_400_BAD_REQUEST:
        raise webhook_bad_request_error

    elif status_code == status.HTTP_401_UNAUTHORIZED:
        raise webhook_unauthorized_error

    elif status_code == status.HTTP_403_FORBIDDEN:
        raise webhook_forbidden_error

    elif status_code == status.HTTP_404_NOT_FOUND:
        raise webhook_not_found_error

    elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        raise webhook_method_not_allowed_error

    elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        raise webhook_too_many_requests_error

    elif status_code == status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS:
        raise webhook_unavailable_for_legal_reasons_error

    else:
        logger.error(e)
        raise internal_server_error