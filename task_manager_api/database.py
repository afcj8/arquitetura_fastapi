"""Conexão com o banco de dados"""

from sqlmodel import Session, SQLModel, create_engine, select
from task_manager_api.security import criar_hash_senha
from task_manager_api.models.usuario import Usuario
from fastapi import Depends

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """Cria as tabelas, se não existirem."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Cria uma sessão com o banco de dados."""
    with Session(engine) as session:
        yield session
        
SessionDep = Depends(get_session)

def create_usuario_admin():
    """Cria um usuário admin padrão, se não existir."""
    with Session(engine) as session:
        usuario_admin = session.exec(select(Usuario).where(Usuario.is_admin == True)).first()
        if not usuario_admin:
            admin = Usuario(
                username="admin",
                senha=criar_hash_senha("admin123"),
                nome="Administrador",
                email="admin@example.com",
                is_admin=True,
            )
            session.add(admin)
            session.commit()