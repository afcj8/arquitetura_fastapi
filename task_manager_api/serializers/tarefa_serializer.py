from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class TarefaRequest(BaseModel):
    """Representa o modelo de criação da tarefa"""
    
    titulo: str
    descricao: Optional[str] = None
    status: str
    prioridade: str
    data_criacao: Optional[datetime] = datetime.now()

class TarefaResponse(BaseModel):
    """Representa o modelo de resposta da tarefa"""
    
    id: int
    titulo: str
    descricao: Optional[str] = None
    status: str
    prioridade: str
    usuario_id: int
    data_criacao: datetime

class TarefaPatchRequest(BaseModel):
    """Representa o modelo de atualização parcial da tarefa"""
    
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None