from datetime import timedelta
from sqlmodel import Session, select
from task_manager_api.database import engine
from task_manager_api.models.usuario import Usuario
from task_manager_api.services.token_service import criar_access_token

from task_manager_api.config import (
    RESET_TOKEN_EXPIRE_MINUTES,
    PWD_RESET_URL,
    smtp_sender
)

MSG_RESET_SENHA = """\
From: API <{sender}>
To: {to}
Assunto: Redefinição de senha

Use o link a seguir para redefinir sua senha:
{url}?token={pwd_reset_token}

Este link expirará em {mens_expire} minutos.
"""


def _enviar_email_debug(email: str, subject: str, msg: str):
    """Simula envio de email escrevendo em arquivo"""
    with open("email.log", "a") as f:
        f.write(
            f"--- EMAIL PARA {email} ---\n"
            f"Subject: {subject}\n"
            f"{msg}\n"
            f"--- FIM DO EMAIL ---\n"
        )


class ResetSenhaService:
    def enviar_reset(self, email: str):
        """Busca o usuário e envia email com token"""

        with Session(engine) as session:
            usuario = session.exec(
                select(Usuario).where(Usuario.email == email)
            ).first()

            if not usuario:
                return  # Não revela que o email não existe

            token = criar_access_token(
                data={"sub": usuario.username},
                expires_delta=timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
                scope="pwd_reset"
            )

            msg = MSG_RESET_SENHA.format(
                sender=smtp_sender,
                to=usuario.nome,
                url=PWD_RESET_URL,
                pwd_reset_token=token,
                mens_expire=RESET_TOKEN_EXPIRE_MINUTES,
            )

            _enviar_email_debug(
                email=usuario.email,
                subject="API - Redefinição de Senha",
                msg=msg,
            )