import urllib.parse

from ..config import constant_settings



def generate_google_oauth_redirect_uri():
    query_params = {
        "redirect_uri": constant_settings.REDIRECT_URI,
        "client_id": constant_settings.OAUTH_GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": " ".join(["openid", "profile", "email"])
    }

    query_string = urllib.parse.urlencode(query=query_params, quote_via=urllib.parse.quote)
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"

    return f"{base_url}?{query_string}"