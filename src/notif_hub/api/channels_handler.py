from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import logging
import httpx

from .channels_helpers import process_channels, handle_http_status_errors
from .texts import generate_channels_response
from .exceptions import internal_server_error, httpx_connect_error
from ..config import configure_logging
from ..auth import get_current_auth_user
from ..database.database import get_async_session
from ..database.managers import psql_manager
from ..database.models import User
from ..basemodels import ChannelsHandlerModel



router = APIRouter(tags=['Channels Handler'], prefix='/api/v1')


configure_logging()
logger = logging.getLogger(__name__)


@router.post('/channels')
async def handle_channels(data: ChannelsHandlerModel) -> dict[str, str]:
    try:
        await process_channels(data)
        return generate_channels_response(data=data)

    except httpx.HTTPStatusError as e:
        handle_http_status_errors(e)

    except httpx.ConnectError as e:
        raise httpx_connect_error

    except HTTPException:
        raise

    except Exception as e:
        logger.error(e)
        raise internal_server_error


@router.post('/channels_auth')
async def handle_auth_channels(
    data: ChannelsHandlerModel,
    current_user: User = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session)
) -> dict[str, str]:
    try:
        data_notification_message, recipient = await process_channels(data)

        user = await psql_manager.get_user_by_username(
            username=current_user.username, session=session
        )

        if not user:    # mypy
            raise internal_server_error

        await psql_manager.add_notification(
            channels=data.targets,
            content=data_notification_message,
            user_id=user.id,
            recipient=recipient,
            session=session
        )

        return generate_channels_response(data=data)

    except httpx.HTTPStatusError as e:
        handle_http_status_errors(e)

    except httpx.ConnectError as e:
        raise httpx_connect_error

    except HTTPException:
        raise

    except Exception as e:
        logger.error(e)
        raise internal_server_error