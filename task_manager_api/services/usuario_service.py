from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.models.usuario import Usuario
from task_manager_api.security import criar_hash_senha
from fastapi.exceptions import HTTPException
from fastapi import status

class UsuarioService:
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    def validar_username_senha(self, usuario: Usuario) -> None:
        if not usuario.username or not usuario.senha:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username e senha são obrigatórios")
        
    def checar_usuario_existente(self, username: str, email: str) -> None:
        usuario_por_username = self.usuario_repository.get_usuario_por_username(username)
        if usuario_por_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username já cadastrado")
        
        usuario_por_email = self.usuario_repository.get_usuario_por_email(email)
        if usuario_por_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado")
        
    def add_usuario(self, usuario: Usuario) -> Usuario:
        self.validar_username_senha(usuario)
        self.checar_usuario_existente(usuario.username, usuario.email)
        usuario.senha = criar_hash_senha(usuario.senha)
        novo_usuario = self.usuario_repository.add_usuario(usuario)
        return novo_usuario