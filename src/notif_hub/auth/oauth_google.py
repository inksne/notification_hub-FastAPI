import urllib.parse
import secrets

from ..config import constant_settings
from ..database.managers import redis_manager



async def generate_google_oauth_redirect_uri():
    state = secrets.token_urlsafe(16)

    await redis_manager.add_state(state=state)

    query_params = {
        "redirect_uri": constant_settings.GOOGLE_REDIRECT_URI,
        "client_id": constant_settings.OAUTH_GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": " ".join(["openid", "profile", "email"]),
        "state": state
    }

    query_string = urllib.parse.urlencode(query=query_params, quote_via=urllib.parse.quote)
    base_url = constant_settings.GOOGLE_AUTH_URL

    return f"{base_url}?{query_string}"