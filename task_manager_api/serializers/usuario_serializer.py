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