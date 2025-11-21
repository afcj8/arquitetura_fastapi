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
        
    def refresh_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            scope = payload.get("scope")

            if not username or scope != "refresh_token":
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
        pwd_reset_token: Optional[str] = None,
    ) -> Usuario:

        usuario_alvo = self.usuario_service.usuario_repository.get_usuario_por_username(username)
        if not usuario_alvo:
            raise HTTPException(404, "Usuário alvo não encontrado")

        if pwd_reset_token:
            try:
                payload = jwt.decode(pwd_reset_token, SECRET_KEY, algorithms=[ALGORITHM])

                if payload.get("sub") != usuario_alvo.username:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Token inválido para o usuário alvo."
                    )
                
                if payload.get("scope") != "pwd_reset":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Token inválido para redefinição de senha."
                    )
                
                return usuario_alvo
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token inválido ou expirado."
                )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Alteração de senha não permitida."
        )