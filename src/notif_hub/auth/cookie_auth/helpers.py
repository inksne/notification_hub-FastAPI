from datetime import datetime, timedelta, timezone
from typing import Any
import secrets
import hashlib

from .schemas import UserSchema
from .utils import encode_jwt
from ...config import auth_settings, constant_settings



def create_jwt(
    token_type: str,
    token_data: dict[str, Any],
    expire_minutes: int = auth_settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload = {constant_settings.TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)

    return encode_jwt(payload=jwt_payload, expire_minutes=expire_minutes, expire_timedelta=expire_timedelta)



def create_access_token(user: UserSchema) -> str:
    jwt_payload = {"sub": user.username}

    return create_jwt(
        token_type=constant_settings.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=auth_settings.auth_jwt.access_token_expire_minutes,
    )



def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def get_refresh_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=auth_settings.auth_jwt.refresh_token_expire_days)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()