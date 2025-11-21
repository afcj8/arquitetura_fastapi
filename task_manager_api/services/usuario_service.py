from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.models.usuario import Usuario

class UsuarioService:
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    def validar_username_senha(self, usuario: Usuario) -> None:
        if not usuario.username or not usuario.senha:
            raise ValueError("Username e senha são obrigatórios.")
        
    def checar_usuario_existente(self, username: str, email: str) -> None:
        usuario_por_username = self.usuario_repository.get_usuario_por_username(username)
        if usuario_por_username:
            raise ValueError("Username já existe.")
        
        if not usuario_por_username:
            raise ValueError("Usuário não encontrado.")
        
        usuario_por_email = self.usuario_repository.get_usuario_por_email(email)
        if usuario_por_email:
            raise ValueError("Email já existe.")
        
    def add_usuario(self, usuario: Usuario) -> Usuario:
        self.validar_username_senha(usuario)
        self.checar_usuario_existente(usuario.username, usuario.email)
        novo_usuario = self.usuario_repository.add_usuario(usuario)
        return novo_usuario