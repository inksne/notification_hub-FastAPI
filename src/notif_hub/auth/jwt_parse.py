from typing import Any

import jwt
from jwt import PyJWKClient

from ..config import constant_settings



_jwk_client: PyJWKClient | None = None


def _get_jwk_client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(constant_settings.GOOGLE_JWKS_URI)

    return _jwk_client


def parse_user_data(data: dict[str, Any]) -> dict[str, Any]:
    id_token = data["id_token"]
    jwk_client = _get_jwk_client()
    signing_key = jwk_client.get_signing_key_from_jwt(id_token)

    return jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=constant_settings.OAUTH_GOOGLE_CLIENT_ID,
        issuer=constant_settings.GOOGLE_ISSUERS,
    )