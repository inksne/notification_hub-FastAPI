from ..basemodels import ChannelsHandlerModel, TelegramHandlerModel, EmailRequestModel, WebhookRequestModel



def generate_channels_response(data: ChannelsHandlerModel) -> dict[str, str]:
    return {
        'msg': f'Сообщение успешно отправлено по каналам: {', '.join(data.channels)}'
    }


def generate_telegram_response(data: TelegramHandlerModel) -> dict[str, str]:
    return {
        'msg': f'Сообщение успешно отправлено пользователю {data.username}.'
    }


def generate_email_response(data: EmailRequestModel) -> dict[str, str]:
    return {
        'msg': f'Сообщение успешно отправлено на {data.to_email}.'
    }


def generate_webhook_response(data: WebhookRequestModel) -> dict[str, str]:
    return {
        'msg': f'Сообщение успешно отправлено на {data.url} в виде {data.form} параметром {data.param_name}.'
    }