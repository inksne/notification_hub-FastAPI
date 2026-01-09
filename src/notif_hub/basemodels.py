from pydantic import BaseModel



class TelegramHandlerModel(BaseModel):
    message: str
    username: str


class ChannelsHandlerModel(BaseModel):
    messages: dict[str, str]
    channels: list[str]
    targets: dict[str, str]


class EmailRequestModel(BaseModel):
    subject: str
    body: str
    to_email: str
    host: str
    port: int
    use_starttls: bool 