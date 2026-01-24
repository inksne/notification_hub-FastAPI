from fastapi import APIRouter

import logging

from .email_helpers import send_email_via_smtp
from .exceptions import internal_server_error
from .texts import generate_email_response
from ..config import configure_logging
from ..basemodels import EmailRequestModel



configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=['Email Handler'], prefix='/api/v1')


@router.post('/email')
async def handle_email_notify(data: EmailRequestModel) -> None:
    try:
        await send_email_via_smtp(data=data)

        return generate_email_response(data=data)

    except Exception as e:
        logger.error(e)
        raise internal_server_error