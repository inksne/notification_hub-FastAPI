from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse
from starlette import status

import logging
import httpx
import jwt
from typing import Any

from ..config import configure_logging, constant_settings
from ..database.managers import redis_manager
from .oauth_google import generate_google_oauth_redirect_uri
from .jwt_parse import parse_user_data
from .exceptions import (
    internal_server_error,
    invalid_response_error,
    invalid_token_error,
    state_not_found_error
)



configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=["Google OAuth"], prefix='/google')



@router.get("/url")
async def get_google_oauth_redirect_uri() -> RedirectResponse:
    uri = await generate_google_oauth_redirect_uri()
    return RedirectResponse(url=uri, status_code=status.HTTP_302_FOUND)


@router.post("/callback")
async def handle_google_code(code: Annotated[str, Body()], state: Annotated[str, Body()]) -> dict[str, dict[str, Any]]:
    if not await redis_manager.get_state(state):
        raise state_not_found_error

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=constant_settings.GOOGLE_TOKEN_URL,
                data={
                    "client_id": constant_settings.OAUTH_GOOGLE_CLIENT_ID,
                    "client_secret": constant_settings.OAUTH_GOOGLE_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "redirect_uri": constant_settings.REDIRECT_URI,
                    "code": code
                }
            )
            response.raise_for_status()

            try:
                data = response.json()

            except ValueError as e:
                logger.error(e)
                raise invalid_response_error

            try:
                return {"user": parse_user_data(data=data)}

            except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                logger.error(e)
                raise invalid_token_error

        except httpx.HTTPStatusError as e:
            logger.error(e)
            raise internal_server_error