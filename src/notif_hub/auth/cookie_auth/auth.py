from fastapi import APIRouter, Depends, Response, Form, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import logging
from datetime import timedelta

from .helpers import create_access_token, create_refresh_token
from .validation import get_current_auth_user_for_refresh, validate_auth_user_db, validate_email
from .utils import hash_password
from .schemas import UserSchema
from ..exceptions import conflict_name_error, bad_email_error, user_exists_error, internal_server_error
from ...database.database import get_async_session
from ...database.models import User
from ...database.managers import psql_manager
from ...config import configure_logging, auth_settings
from ...basemodels import TokenInfo



configure_logging()
logger = logging.getLogger(__name__)


http_bearer = HTTPBearer(auto_error=False)


router = APIRouter(prefix='/jwt', tags=["JWT"], dependencies=[Depends(http_bearer)])


@router.post('/register')
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:
    try:
        new_user = await psql_manager.register(
            username=username,
            email=validate_email(email),
            hashed_password=hash_password(password).decode('utf-8'),
            session=session
        )

        if new_user is False:
            raise user_exists_error

        if new_user is None:
            raise conflict_name_error

        return RedirectResponse('/jwt/login', status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException:
        raise bad_email_error

    except Exception as e:
        logger.error(e)
        raise internal_server_error


@router.post('/login', response_model=TokenInfo)
async def auth_user_issue_jwt(response: Response, user: UserSchema = Depends(validate_auth_user_db)) -> TokenInfo:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=False,
        max_age=int(timedelta(minutes=auth_settings.auth_jwt.access_token_expire_minutes).total_seconds())
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=False,
        secure=False,
        max_age=int(timedelta(days=auth_settings.auth_jwt.refresh_token_expire_days).total_seconds())
    )

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh_jwt(current_user: UserSchema = Depends(get_current_auth_user_for_refresh)) -> JSONResponse:
    new_access_token = create_access_token(current_user)
    response = JSONResponse(content={"access_token": new_access_token})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=False,
        secure=False,
        max_age=int(timedelta(minutes=auth_settings.auth_jwt.access_token_expire_minutes).total_seconds())
    )

    return response


@router.post('/logout')
async def logout(response: Response) -> RedirectResponse:
    response = RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token", httponly=False, secure=False)
    response.delete_cookie(key="refresh_token", httponly=False, secure=False)

    return response