from fastapi import HTTPException
from starlette import status



internal_server_error = HTTPException(
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Непредвиденная серверная ошибка. Повторите попытку позже.'
)


invalid_response_error = HTTPException(
    status.HTTP_502_BAD_GATEWAY,
    detail='Невалидный формат данных от провайдера Oauth.'
)


invalid_token_error = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    detail='Проблема декодирования jwt токена.'
)