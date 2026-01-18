from fastapi import APIRouter

import logging

from ..config import configure_logging
from .oauth_google import generate_google_oauth_redirect_uri



configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=["Auth"])



@router.get("/google/url")
def get_foofle_oauth_redirect_uri():
    uri = generate_google_oauth_redirect_uri()

    return uri