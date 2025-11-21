from pydantic import BaseModel

class AuthRequest(BaseModel):
    """Representa o modelo de dados para autenticação de usuário."""
    
    username: str
    senha: str