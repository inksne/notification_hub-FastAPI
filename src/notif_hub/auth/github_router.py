from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import strategies
from starlette import status

import logging
import httpx
from typing import Any

from ..config import configure_logging, constant_settings
from ..database.managers import redis_manager
from .oauth_github import generate_github_oauth_redirect_uri
from .exceptions import (
    internal_server_error,
    invalid_response_error,
    state_not_found_error
)



configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=["Auth"], prefix='/github')



@router.get("/url")
async def get_github_oauth_redirect_uri() -> RedirectResponse:
    uri = await generate_github_oauth_redirect_uri()
    return RedirectResponse(url=uri, status_code=status.HTTP_302_FOUND)




@router.post("/callback")
async def handle_github_code(code: Annotated[str, Body()], state: Annotated[str, Body()]) -> dict[str, dict[str, Any]]:
    if not await redis_manager.get_state(state):
        raise state_not_found_error

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Accept": "application/json"}

            response = await client.post(
                url=constant_settings.GITHUB_TOKEN_URL,
                data={
                    "client_id": constant_settings.OAUTH_GITHUB_CLIENT_ID,
                    "client_secret": constant_settings.OAUTH_GITHUB_CLIENT_SECRET,
                    "redirect_uri": constant_settings.REDIRECT_URI,
                    "code": code
                },
                headers=headers
            )
            response.raise_for_status()

            try:
                data = response.json()

            except ValueError as e:
                logger.error(e)
                raise invalid_response_error

            access_token = data.get("access_token")

            if not access_token:
                raise invalid_response_error

            user_response = await client.get(
                url=constant_settings.GITHUB_ACCESS_URL,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {access_token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            user_response.raise_for_status()

            try:
                return {"user": user_response.json()}

            except ValueError as e:
                logger.error(e)
                raise invalid_response_error

        except httpx.HTTPStatusError as e:
            logger.error(e)
            raise internal_server_error