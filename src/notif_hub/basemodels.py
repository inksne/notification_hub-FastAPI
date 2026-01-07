from pydantic import BaseModel



class TelegramHandlerModel(BaseModel):
    message: str
    username: str