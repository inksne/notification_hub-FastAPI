from fastapi import APIRouter
from starlette import status

import logging
import httpx

from .exceptions import (
    internal_server_error,
    webhook_bad_request_error,
    webhook_unauthorized_error,
    webhook_forbidden_error,
    webhook_not_found_error,
    webhook_method_not_allowed_error,
    webhook_too_many_requests_error,
    webhook_unavailable_for_legal_reasons_error
)
from ..basemodels import WebhookRequestModel
from ..config import configure_logging



configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=['Webhook Handler'], prefix='/api/v1')


@router.post('/webhook', status_code=status.HTTP_204_NO_CONTENT)
async def handle_webhook_notify(data: WebhookRequestModel) -> None:
    async with httpx.AsyncClient() as client:
        try:
            if data.format == 'json':
                headers = {"Content-Type": "application/json"}

                json_data = {
                    data.param_name: data.message
                }

                response = await client.post(url=data.url, json=json_data, headers=headers)

            elif data.format == 'form':
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                response = await client.post(url=f'{data.url}&{data.param_name}={data.message}', headers=headers)

            else:
                headers = {"Content-Type": "text/plain; charset=utf-8"}

                response = await client.post(url=data.url, content=data.message, headers=headers)

            response.raise_for_status()

        except httpx.HTTPStatusError as e:
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