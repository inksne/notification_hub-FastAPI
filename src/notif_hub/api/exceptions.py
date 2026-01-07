from fastapi import HTTPException
from starlette import status



internal_server_error = HTTPException(
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Непредвиденная серверная ошибка. Повторите попытку позже.'
)


telegram_forbidden_error = HTTPException(
    status.HTTP_403_FORBIDDEN,
    detail='Невозможно отправить сообщению пользователю. Скорее всего он не начал диалог с ботом, либо заблокировал бота.'
)


telegram_retry_after_error = HTTPException(
    status.HTTP_429_TOO_MANY_REQUESTS,
    detail='Слишком много запросов с данного IP адреса. Повторите попытку позже.'
)