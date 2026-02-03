from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse
from sqlalchemy.ext.asyncio import AsyncSession

import logging
from pathlib import Path

from ..config import auth_settings, configure_logging
from ..auth import get_current_auth_user
from ..database.database import get_async_session
from ..database.managers import psql_manager
from ..database.models import User, Notification

configure_logging()
log = logging.getLogger(__name__)


router = APIRouter(tags=['Templates'])


templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent))



@router.get("/", response_class=HTMLResponse)
async def get_base_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "base.html")


@router.get("/about", response_class=HTMLResponse)
async def get_about_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "about_us.html")


@router.get("/jwt/register", response_class=HTMLResponse)
async def get_register_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "register.html")


@router.get("/jwt/login", response_class=HTMLResponse)
async def get_login_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "login.html")


@router.get("/authenticated", response_class=HTMLResponse)
async def get_authenticated_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(
        request, "authenticated.html", {
            "ACCESS_TOKEN_LIFETIME": auth_settings.auth_jwt.access_token_expire_minutes * 60000 # ms
        }
    )


@router.get("/authenticated/notifications", response_class=HTMLResponse)
async def get_notifications_page(
    request: Request, current_user: User = Depends(get_current_auth_user)
) -> _TemplateResponse:
    return templates.TemplateResponse(
        request, "notifications.html", {
            "ACCESS_TOKEN_LIFETIME": auth_settings.auth_jwt.access_token_expire_minutes * 60000 # ms
        }
    )


@router.get("/authenticated/notifications/get_all_notifications", response_model=None)
async def get_all_notifications(
    current_user: User = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session)
) -> list[Notification]:
    notifications = await psql_manager.get_notifications(user_id=current_user.id, session=session)

    return notifications


@router.post("/authenticated/notifications/add_notification")
async def add_notification(
    channels: list[str],
    content: str,
    current_user: User = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    await psql_manager.add_notification(channels=channels, content=content, user_id=current_user.id, session=session)


@router.delete("/authenticated/notifications/delete_notification")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    await psql_manager.delete_notification(notification_id=notification_id, session=session)