from fastapi import APIRouter, Depends
from task_manager_api.database import get_session
from sqlmodel import Session

from task_manager_api.models.usuario import Usuario
from task_manager_api.dependencies import get_usuario_autenticado, pode_alterar_senha
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.serializers.usuario_serializer import (
    UsuarioRequest, 
    UsuarioResponse, 
    UsuarioPatchRequest, 
    UsuarioSenhaPatchRequest
)

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

@router.get(
    "/me",
    response_model=UsuarioResponse
)
def obter_usuario_atual(
    usuario: Usuario = Depends(get_usuario_autenticado)
):
    return usuario

@router.patch("/{id}")
def atualizar_usuario(
    id: int,
    usuario_data: UsuarioPatchRequest,
    session: Session = Depends(get_session),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
):
    repo = UsuarioRepository(session)
    service = UsuarioService(repo)
    usuario = service.update_usuario(id, usuario_data, usuario_logado)
    
    return {"detail": "Usuário atualizado com sucesso.", "usuario_id": usuario.id}

@router.patch("/{username}/senha")
def alterar_senha_usuario(
    username: str,
    senha_data: UsuarioSenhaPatchRequest,
    usuario: Usuario = Depends(pode_alterar_senha),
    session: Session = Depends(get_session),
):
    repo = UsuarioRepository(session)
    service = UsuarioService(repo)

    usuario_atualizado = service.update_senha_usuario(
        usuario,
        senha_data
    )

    return {"detail": "Senha alterada com sucesso.", "usuario_id": usuario_atualizado.id}