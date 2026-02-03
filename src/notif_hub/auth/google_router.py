from typing import Annotated
from fastapi import APIRouter, Body, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

import logging
import httpx
import jwt
from datetime import timedelta

from ..config import configure_logging, constant_settings, auth_settings
from ..database.managers import redis_manager, psql_manager
from ..database.database import get_async_session
from .oauth_google import generate_google_oauth_redirect_uri
from .jwt_parse import parse_user_data
from .cookie_auth.helpers import create_access_token, create_refresh_token
from .cookie_auth.schemas import UserSchema
from .cookie_auth.utils import hash_password
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
async def handle_google_code(
    code: Annotated[str, Body()],
    state: Annotated[str, Body()],
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    if not await redis_manager.get_state(state):
        raise state_not_found_error

    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(
                url=constant_settings.GOOGLE_TOKEN_URL,
                data={
                    "client_id": constant_settings.OAUTH_GOOGLE_CLIENT_ID,
                    "client_secret": constant_settings.OAUTH_GOOGLE_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "redirect_uri": constant_settings.REDIRECT_URI,
                    "code": code
                }
            )
            token_response.raise_for_status()

            try:
                token_data = token_response.json()

            except ValueError as e:
                logger.error(e)
                raise invalid_response_error

            try:
                user_data = parse_user_data(data=token_data)
                logger.info(user_data)

                email = user_data.get("email")
                if not email:
                    raise invalid_response_error

                username = email

                oauth_password_hash = hash_password(f"oauth_{email}_{constant_settings.OAUTH_GOOGLE_CLIENT_ID[:45]}").decode('utf-8')
                db_user = await psql_manager.get_or_create_oauth_user(
                    email=email,
                    username=username,
                    hashed_password=oauth_password_hash,
                    session=session
                )

                if not db_user:
                    raise invalid_response_error

                user_schema = UserSchema.from_attributes(db_user)

                access_token = create_access_token(user_schema)
                refresh_token = create_refresh_token(user_schema)

                resp = JSONResponse(content={"user": user_data})
                resp.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=False,
                    secure=False,
                    max_age=int(
                        timedelta(
                            minutes=auth_settings.auth_jwt.access_token_expire_minutes
                        ).total_seconds()
                    ),
                )
                resp.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=False,
                    secure=False,
                    max_age=int(
                        timedelta(
                            days=auth_settings.auth_jwt.refresh_token_expire_days
                        ).total_seconds()
                    ),
                )

                return resp

            except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                logger.error(e)
                raise invalid_token_error

        except httpx.HTTPStatusError as e:
            logger.error(e)
            raise internal_server_error