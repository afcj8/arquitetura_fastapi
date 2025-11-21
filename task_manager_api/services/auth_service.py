from jose import JWTError, jwt
from fastapi import HTTPException, status

from task_manager_api.config import SECRET_KEY, ALGORITHM
from task_manager_api.security import verificar_senha
from task_manager_api.services.usuario_service import UsuarioService

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
    
    def decodificar_token(self, token: str):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise CREDENCIAIS_INVALIDAS