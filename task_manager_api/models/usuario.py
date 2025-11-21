"""Modelos de dados relacionados ao usuário"""

from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
from task_manager_api.security import HashedPassword

class Usuario(SQLModel, table=True):
    """Representa o modelo do usuário"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    nome: str = Field(nullable=False)
    senha: HashedPassword
    email: str = Field(unique=True, nullable=False)
    data_criacao: datetime = Field(default=datetime.now())