"""Repositório para operações relacionadas ao usuário."""

from task_manager_api.models.usuario import Usuario
from .tarefa_repository import TarefaRepository
from sqlmodel import Session, select

class UsuarioRepository:    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_usuario_por_username(self, username: str) -> Usuario | None:
        usuario = self.db_session.exec(select(Usuario).where(Usuario.username == username)).first()
        return usuario
    
    def get_usuario_por_username_excluindo_id(self, username: str, usuario_id: int) -> Usuario | None:
        usuario = self.db_session.exec(
            select(Usuario).where(Usuario.username == username, Usuario.id != usuario_id)
        ).first()
        return usuario

    def get_usuario_por_email(self, email: str) -> Usuario | None:
        usuario = self.db_session.exec(select(Usuario).where(Usuario.email == email)).first()
        return usuario
    
    def get_usuario_por_email_excluindo_id(self, email: str, usuario_id: int) -> Usuario | None:
        usuario = self.db_session.exec(
            select(Usuario).where(Usuario.email == email, Usuario.id != usuario_id)
        ).first()
        return usuario

    def get_usuario_por_id(self, usuario_id: int) -> Usuario | None:
        usuario = self.db_session.get(Usuario, usuario_id)
        return usuario
    
    def get_admin(self, username: str) -> Usuario | None:
        usuario = self.db_session.exec(
            select(Usuario).where(
                Usuario.is_admin == True,
                Usuario.username == username    
            )).first()
        return usuario
    
    def get_admins(self) -> list[Usuario]:
        admins = self.db_session.exec(
            select(Usuario).where(Usuario.is_admin == True)
        ).all()
        return admins
    
    def get_usuarios(self) -> list[Usuario]:
        usuarios = self.db_session.exec(select(Usuario)).all()
        return usuarios

    def add_update_usuario(self, usuario: Usuario) -> Usuario:
        self.db_session.add(usuario)
        self.db_session.commit()
        self.db_session.refresh(usuario)
        return usuario
    
    def delete_usuario(self, usuario: Usuario) -> None:
        tarefa_repository = TarefaRepository(self.db_session)
        tarefas_usuario = tarefa_repository.get_tarefas_por_usuario_id(usuario.id)
        for tarefa in tarefas_usuario:
            tarefa_repository.delete_tarefa(tarefa)
        
        self.db_session.delete(usuario)
        self.db_session.commit()