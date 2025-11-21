from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from task_manager_api.database import get_session
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.services.auth_service import AuthService
from task_manager_api.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_usuario_service(session=Depends(get_session)):
    return UsuarioService(UsuarioRepository(session))

def get_auth_service(usuario_service=Depends(get_usuario_service)):
    return AuthService(usuario_service)

def get_usuario_autenticado(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.validar_token(token)


def pode_alterar_senha(
    username: str,
    pwd_reset_token: Optional[str] = None,
    auth_service: AuthService = Depends(get_auth_service),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
) -> Usuario:
    """
    Retorna o usuário-alvo SE e SOMENTE SE o usuário logado
    puder alterar a senha dele.
    """
    
    return auth_service.get_usuario_se_alterar_senha_for_permitido(
        username=username,
        usuario_logado=usuario_logado,
        pwd_reset_token=pwd_reset_token
    )