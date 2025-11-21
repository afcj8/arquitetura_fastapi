from fastapi import APIRouter, Depends
from task_manager_api.database import get_session
from sqlmodel import Session

from task_manager_api.models.usuario import Usuario
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.serializers.usuario_serializer import UsuarioRequest

router = APIRouter()

@router.post("")
def criar_usuario(
    usuario_data: UsuarioRequest,
    session: Session = Depends(get_session)
):
    repo = UsuarioRepository(session)
    service = UsuarioService(repo)
    usuario = Usuario.model_validate(usuario_data)
    novo_usuario = service.add_usuario(usuario)
    return {"detail": "Usuário criado com sucesso.", "usuario_id": novo_usuario.id}