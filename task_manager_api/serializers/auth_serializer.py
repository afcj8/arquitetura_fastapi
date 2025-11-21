from pydantic import BaseModel, model_validator

class AuthRequest(BaseModel):
    """Representa o modelo de dados para autenticação de usuário."""
    
    username: str
    senha: str