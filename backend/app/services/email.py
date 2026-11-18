"""Envio de e-mail (T-026).

Em desenvolvimento o backend padrão é `console`: o conteúdo do e-mail é
registrado no log da aplicação. Em produção, configure `EMAIL_BACKEND=smtp`
e as variáveis SMTP correspondentes.
"""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    if settings.email_backend == "smtp":
        message = EmailMessage()
        message["From"] = settings.email_from
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        return

    logger.info("E-mail (console) para %s | Assunto: %s\n%s", to, subject, body)


def send_password_reset(to: str, token: str) -> None:
    link = f"{settings.frontend_base_url}/redefinir-senha?token={token}"
    body = (
        "Olá!\n\n"
        "Recebemos uma solicitação de redefinição de senha no meuSaldo.\n\n"
        f"Para definir uma nova senha, acesse o link: {link}\n\n"
        f"O link expira em {settings.reset_token_expire_minutes} minutos.\n"
        "Se você não solicitou esta redefinição, ignore este e-mail.\n"
    )
    send_email(to, "meuSaldo — Redefinição de senha", body)
