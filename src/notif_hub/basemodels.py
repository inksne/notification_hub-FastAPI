from pydantic import BaseModel
from typing import Union, Final
from pathlib import Path



class TelegramHandlerModel(BaseModel):
    message: str
    username: str


class ChannelsHandlerModel(BaseModel):
    messages: dict[str, str]
    channels: list[str]
    targets: dict[str, Union[str, dict]]


class EmailRequestModel(BaseModel):
    body: str
    to_email: str


class WebhookRequestModel(BaseModel):
    message: str
    url: str
    format: str
    param_name: str


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"