from fastapi import APIRouter, Depends, Response, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import logging
from datetime import datetime, timedelta, timezone

from .helpers import (
    create_access_token,
    create_refresh_token,
    get_refresh_expires_at,
    hash_refresh_token,
)
from .validation import get_current_auth_user, validate_auth_user_db, validate_email
from .utils import hash_password
from .schemas import UserSchema
from ..exceptions import (
    conflict_name_error,
    bad_email_error,
    user_exists_error,
    not_found_refresh_token_error,
    internal_server_error
)
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
async def auth_user_issue_jwt(
    response: Response,
    user: UserSchema = Depends(validate_auth_user_db),
    session: AsyncSession = Depends(get_async_session),
) -> TokenInfo:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token()

    expires_at = get_refresh_expires_at()
    refresh_token_hash = hash_refresh_token(refresh_token)

    await psql_manager.add_refresh_token_hash(
        username=user.username,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
        session=session
    )

    access_max_age = int(timedelta(minutes=auth_settings.auth_jwt.access_token_expire_minutes).total_seconds())
    refresh_max_age = int(timedelta(days=auth_settings.auth_jwt.refresh_token_expire_days).total_seconds())

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=False,
        max_age=access_max_age,
        expires=datetime.now(timezone.utc) + timedelta(seconds=access_max_age)
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=False,
        secure=False,
        max_age=refresh_max_age,
        expires=datetime.now(timezone.utc) + timedelta(seconds=refresh_max_age)
    )

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh_jwt(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
) -> TokenInfo:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise not_found_refresh_token_error

    refresh_token_hash = hash_refresh_token(refresh_token)

    now = datetime.now(timezone.utc)

    db_refresh_token_hash = await psql_manager.get_refresh_token_hash(
        refresh_token_hash=refresh_token_hash,
        now=now,
        session=session
    )

    if not db_refresh_token_hash:    # mypy
        raise not_found_refresh_token_error

    db_user = await psql_manager.get_user_by_user_id(
        user_id=db_refresh_token_hash.user_id,
        session=session
    )

    current_user = UserSchema.from_attributes(db_user)
    new_access_token = create_access_token(current_user)
    new_refresh_token = create_refresh_token()

    now = datetime.now(timezone.utc)

    await psql_manager.update_refresh_token_hash(
        refresh_token_hash=db_refresh_token_hash.refresh_token_hash,
        now=now,
        new_refresh_token_hash=hash_refresh_token(new_refresh_token),
        new_expires_at=get_refresh_expires_at(),
        session=session
    )

    access_max_age = int(timedelta(minutes=auth_settings.auth_jwt.access_token_expire_minutes).total_seconds())
    refresh_max_age = int(timedelta(days=auth_settings.auth_jwt.refresh_token_expire_days).total_seconds())

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=False,
        secure=False,
        max_age=access_max_age,
        expires=datetime.now(timezone.utc) + timedelta(seconds=access_max_age)
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=False,
        secure=False,
        max_age=refresh_max_age,
        expires=datetime.now(timezone.utc) + timedelta(seconds=refresh_max_age)
    )

    return TokenInfo(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post('/logout')
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise not_found_refresh_token_error

    refresh_token_hash = hash_refresh_token(refresh_token)

    now = datetime.now(timezone.utc)

    db_refresh_token_hash = await psql_manager.get_refresh_token_hash(
        refresh_token_hash=refresh_token_hash,
        now=now,
        session=session
    )

    if db_refresh_token_hash:
        await psql_manager.delete_refresh_token_hash(
            db_refresh_token_hash=db_refresh_token_hash,
            session=session
        )

    response = RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)

    response.delete_cookie(key="access_token", httponly=False, secure=False)
    response.delete_cookie(key="refresh_token", httponly=False, secure=False)

    return response


@router.get('/check_tokens')
async def check_token(
    current_user: User = Depends(get_current_auth_user)
) -> RedirectResponse:
    '''
    Если пользователь не авторизован, то его не перекинет на страницу авторизации
    Если у пользователя в куки имеются access и refresh токены, и они валидны, то его перекинет на /authenticated
    '''
    return RedirectResponse('/authenticated', status.HTTP_303_SEE_OTHER)