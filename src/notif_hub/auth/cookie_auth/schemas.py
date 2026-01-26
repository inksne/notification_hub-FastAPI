from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, Any

from ..exceptions import bad_email_error



class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)
    username: str
    password: str | bytes
    email: Optional[EmailStr] = None

    @classmethod
    def from_attributes(cls, obj: Any) -> "UserSchema":
        return cls(
            username=obj.username,
            password=obj.password,
            email=obj.email,
        )

    @field_validator('email', mode='before')
    def check_email(cls, email: str) -> str:
        if email in [None, '', 'null'] or '@' not in email or '.' not in email:
            raise bad_email_error

        return email