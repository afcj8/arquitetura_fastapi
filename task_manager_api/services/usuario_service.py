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
        
    def add_update_usuario(self, usuario: Usuario) -> Usuario:
        self.validar_username_senha(usuario)
        self.checar_usuario_existente(usuario.username, usuario.email)
        usuario.senha = criar_hash_senha(usuario.senha)
        novo_usuario = self.usuario_repository.add_update_usuario(usuario)
        return novo_usuario
    
    def update_usuario(self, usuario_id: int, usuario_atualizado: Usuario, usuario_logado: Usuario) -> Usuario:

        usuario_existente = self.usuario_repository.get_usuario_por_id(usuario_id)

        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        if usuario_existente.id != usuario_logado.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para atualizar este usuário."
            )

        if usuario_atualizado.username and usuario_atualizado.username != usuario_existente.username:
            self.checar_usuario_existente(usuario_atualizado.username, usuario_existente.email)
            usuario_existente.username = usuario_atualizado.username
        
        if usuario_atualizado.email and usuario_atualizado.email != usuario_existente.email:
            self.checar_usuario_existente(usuario_existente.username, usuario_atualizado.email)
            usuario_existente.email = usuario_atualizado.email
        
        usuario_existente.nome = usuario_atualizado.nome or usuario_existente.nome
        self.usuario_repository.db_session.add(usuario_existente)
        self.usuario_repository.db_session.commit()
        self.usuario_repository.db_session.refresh(usuario_existente)

        return usuario_existente