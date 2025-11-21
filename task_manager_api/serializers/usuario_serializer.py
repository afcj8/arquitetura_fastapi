from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UsuarioRequest(BaseModel):
    """Representa o modelo de criação do usuário"""
    
    username: str
    nome: str
    senha: str
    email: str
    data_criacao: Optional[datetime] = datetime.now()

class UsuarioResponse(BaseModel):
    """Representa o modelo de resposta do usuário"""
    
    id: int
    username: str
    nome: str
    email: str
    data_criacao: datetime

class UsuarioPatchRequest(BaseModel):
    """Representa o modelo de atualização parcial do usuário"""
    
    username: Optional[str] = None
    nome: Optional[str] = None
    email: Optional[str] = None