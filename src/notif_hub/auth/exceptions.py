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


state_not_found_error = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    detail='Время, отведённое на авторизацию, истекло. Попробуйте снова.'
)


bad_email_error = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail='Email некорректен. Введите действительный адрес электронной почты.'
)


bad_token_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail=f'Неверный токен.',
)


not_found_access_token_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access токен не найден в куки.",
)


not_found_refresh_token_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Refresh токен не найден в куки.",
)


not_found_token_user_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Неверный токен.',
)


unauthed_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный логин или пароль."
)


conflict_name_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Данное имя пользователя уже используется. Попробуйте другое.'
)


user_exists_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Пользователь с такими данными уже существует.'
)