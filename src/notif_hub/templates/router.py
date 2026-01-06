from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse

import logging
from pathlib import Path

from ..database.models import User

from ..config import configure_logging


configure_logging()
log = logging.getLogger(__name__)


router = APIRouter(tags=['Templates'])


templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent))



@router.get("/", response_class=HTMLResponse)
async def get_base_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "base.html")