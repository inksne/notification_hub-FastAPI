from pydantic import BaseModel



class TelegramHandlerModel(BaseModel):
    message: str
    username: str


class ChannelsHandlerModel(BaseModel):
    messages: dict[str, str]
    channels: list[str]
    targets: dict[str, str]