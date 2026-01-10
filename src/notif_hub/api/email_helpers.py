from email.message import EmailMessage

import aiosmtplib
import ssl

from ..config import EMAIL_SENDER_ADDRESS, EMAIL_SUBJECT, EMAIL_PASSWORD, EMAIL_HOST, EMAIL_PORT
from ..basemodels import EmailRequestModel


def build_email_message(
    body: str,
    to_email: str,
) -> EmailMessage:

    message = EmailMessage()
    message["From"] = EMAIL_SENDER_ADDRESS
    message["To"] = to_email
    message["Subject"] = EMAIL_SUBJECT
    message.set_content(body)

    return message


# async def send_email_via_maildev(
#     subject: str,
#     body: str,
#     to_email: str,
#     host: str = "127.0.0.1",
#     port: int = 1025,
# ) -> None:
#     message = build_email_message(
#         subject=subject,
#         body=body,
#         to_email=to_email,
#     )

#     await aiosmtplib.send(message, hostname=host, port=port)


async def send_email_via_smtp(data: EmailRequestModel) -> None:
    message = build_email_message(
        body=data.body,
        to_email=data.to_email,
    )

    ssl_context = ssl.create_default_context()

    await aiosmtplib.send(
        message,
        hostname=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_SENDER_ADDRESS,
        password=EMAIL_PASSWORD,
        use_tls=True,
        tls_context=ssl_context,
    )