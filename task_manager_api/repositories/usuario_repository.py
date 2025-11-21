"""Repositório para operações relacionadas ao usuário."""

from task_manager_api.models.usuario import Usuario
from sqlmodel import Session, select

class UsuarioRepository:    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_usuario_por_username(self, username: str) -> Usuario | None:
        usuario = self.db_session.exec(select(Usuario).where(Usuario.username == username)).first()
        return usuario

    def get_usuario_por_email(self, email: str) -> Usuario | None:
        usuario = self.db_session.exec(select(Usuario).where(Usuario.email == email)).first()
        return usuario

    def get_usuario_por_id(self, usuario_id: int) -> Usuario | None:
        usuario = self.db_session.get(Usuario, usuario_id)
        return usuario

    def add_update_usuario(self, usuario: Usuario) -> Usuario:
        self.db_session.add(usuario)
        self.db_session.commit()
        self.db_session.refresh(usuario)
        return usuario