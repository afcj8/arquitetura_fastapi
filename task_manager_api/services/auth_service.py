from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from task_manager_api.config import SECRET_KEY, ALGORITHM
from task_manager_api.security import verificar_senha
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.models.usuario import Usuario

CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas.",
    headers={"WWW-Authenticate": "Bearer"},
)

class AuthService:
    def __init__(self, usuario_service: UsuarioService):
        self.usuario_service = usuario_service

    def autenticar_usuario(self, username: str, senha: str):
        usuario = self.usuario_service.usuario_repository.get_usuario_por_username(username)
        
        if not usuario:
            raise CREDENCIAIS_INVALIDAS
        
        if not verificar_senha(senha, usuario.senha):
            raise CREDENCIAIS_INVALIDAS

        return usuario
        
    def validar_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")

            if not username:
                raise CREDENCIAIS_INVALIDAS

            usuario = self.usuario_service.usuario_repository.get_usuario_por_username(username)
            if not usuario:
                raise CREDENCIAIS_INVALIDAS

            return usuario

        except JWTError:
            raise CREDENCIAIS_INVALIDAS
        
    def get_usuario_se_alterar_senha_for_permitido(
        self,
        username: str,
        usuario_logado: Usuario,
        pwd_reset_token: Optional[str] = None,
    ) -> Usuario:

        usuario_alvo = self.usuario_service.usuario_repository.get_usuario_por_username(username)
        if not usuario_alvo:
            raise HTTPException(404, "Usuário alvo não encontrado")

        # Se foi enviado token de reset
        usuario_token = None
        if pwd_reset_token:
            usuario_token = self.validar_token(pwd_reset_token)

        validar_reset = usuario_token and usuario_token.id == usuario_alvo.id
        validar_logado = usuario_logado.id == usuario_alvo.id

        if not validar_reset and not validar_logado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para alterar a senha deste usuário."
            )
        return usuario_alvo