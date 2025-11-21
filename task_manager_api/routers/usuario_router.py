from fastapi import APIRouter, Depends
from task_manager_api.database import get_session
from sqlmodel import Session

from task_manager_api.models.usuario import Usuario
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.services.usuario_service import UsuarioService

router = APIRouter()

@router.post("")
def criar_usuario(usuario: Usuario, usuario_service: UsuarioService = Depends(
    lambda session=Depends(get_session): UsuarioService(UsuarioRepository(session))
)):
    novo_usuario = usuario_service.add_usuario(usuario)
    return novo_usuario