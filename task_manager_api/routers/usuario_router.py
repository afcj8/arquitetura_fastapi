from typing import Optional
from sqlmodel import Session
from fastapi import APIRouter, Depends
from task_manager_api.database import get_session
from fastapi import APIRouter, BackgroundTasks, Body
from task_manager_api.models.usuario import Usuario
from task_manager_api.dependencies import get_usuario_autenticado, get_auth_service
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.services.auth_service import AuthService
from task_manager_api.services.reset_senha_service import ResetSenhaService
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

@router.post("/reset-senha")
def solicitar_reset_senha(
    email: str = Body(embed=True),
    background_tasks: BackgroundTasks = None,
):
    """
    Envia um email para reset de senha.
    Não revela se o email existe ou não.
    """
    service = ResetSenhaService()

    background_tasks.add_task(service.enviar_reset, email)

    return {"detail": "Se o email existir, o link será enviado."}

@router.patch("/{username}/senha")
def alterar_senha_usuario(
    username: str,
    senha_data: UsuarioSenhaPatchRequest,
    pwd_reset_token: Optional[str] = None,
    session: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    usuario = auth_service.get_usuario_se_alterar_senha_for_permitido(
        username=username,
        pwd_reset_token=pwd_reset_token,
    )

    repo = UsuarioRepository(session)
    service = UsuarioService(repo)

    usuario_atualizado = service.update_senha_usuario(
        usuario.id,
        senha_data,
        usuario
    )

    return {"detail": "Senha alterada com sucesso.", "id": usuario_atualizado.id}