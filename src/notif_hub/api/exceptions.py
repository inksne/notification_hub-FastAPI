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


webhook_bad_request_error = HTTPException(
    status.HTTP_400_BAD_REQUEST,
    detail='Ошибка в запросе. Скорее всего сервер не принимает сообщения с указанным параметром или в указанной форме.'
)


webhook_unauthorized_error = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    detail='Для отправки сообщения на указанный url необходимо пройти аутентификацию.'
)


webhook_forbidden_error = HTTPException(
    status.HTTP_403_FORBIDDEN,
    detail='Недостаточно прав для отправки сообщения на указанный url (Политика получателя).'
)


webhook_not_found_error = HTTPException(
    status.HTTP_404_NOT_FOUND,
    detail='Запрашиваемый ресрус не найден. Возможно, ошибка в написании url.'
)


webhook_method_not_allowed_error = HTTPException(
    status.HTTP_405_METHOD_NOT_ALLOWED,
    detail='Метод запроса не разрешен для указанного url. Возможно, сервер не поддерживает POST запросы.'
)


webhook_too_many_requests_error = HTTPException(
    status.HTTP_429_TOO_MANY_REQUESTS,
    detail='Вы отправили слишком много запросов на указанный url. Повторите попытку позже.'
)


webhook_unavailable_for_legal_reasons_error = HTTPException(
    status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
    detail='Запрашиваемый ресурс не может предоставлен по закону.'
)