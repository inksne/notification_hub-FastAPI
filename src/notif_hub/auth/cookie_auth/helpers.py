from datetime import timedelta
from typing import Any

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



def create_refresh_token(user: UserSchema) -> str:
    jwt_payload = {"sub": user.username}

    return create_jwt(
        token_type=constant_settings.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=auth_settings.auth_jwt.refresh_token_expire_days)
    )