"""Modelos de dados relacionados a tarefa"""

from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    PENDENTE = "pendente"
    EM_PROGRESSO = "em_progresso"
    CONCLUIDA = "concluida"

class PrioridadeEnum(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"

class Tarefa(SQLModel, table=True):
    """Representa o modelo do usuário"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(nullable=False)
    descricao: Optional[str] = Field(default=None)
    status: StatusEnum = Field(nullable=False)
    prioridade: PrioridadeEnum = Field(nullable=False)
    usuario_id: int = Field(foreign_key="usuario.id", nullable=False)
    data_criacao: datetime = Field(default=datetime.now())