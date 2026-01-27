from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse

import logging
from pathlib import Path

from ..config import configure_logging


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


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "register.html")


@router.get("/authenticated", response_class=HTMLResponse)
async def get_authenticated_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "authenticated.html")