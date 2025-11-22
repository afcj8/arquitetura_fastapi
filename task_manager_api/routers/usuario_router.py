from typing import Optional
from fastapi import APIRouter, Depends
from fastapi import APIRouter, BackgroundTasks, Body
from task_manager_api.models.usuario import Usuario
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.services.auth_service import AuthService
from task_manager_api.services.reset_senha_service import ResetSenhaService
from task_manager_api.dependencies import (
    get_usuario_autenticado, 
    get_usuario_service, 
    get_auth_service
)
from task_manager_api.serializers.usuario_serializer import (
    UsuarioRequest, 
    UsuarioResponse,
    UsuarioAdminResponse,
    UsuarioPatchRequest, 
    UsuarioSenhaPatchRequest
)

router = APIRouter()

@router.get(
    "",
    response_model=list[UsuarioAdminResponse]
)
def listar_usuarios(
    service: UsuarioService = Depends(get_usuario_service),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
):    
    usuarios = service.get_usuarios(usuario_logado)
    return usuarios

@router.post("")
def criar_usuario(
    usuario_data: UsuarioRequest,
    service: UsuarioService = Depends(get_usuario_service)
):
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

@router.get(
    "/{id}",
    response_model=UsuarioAdminResponse
)
def obter_usuario_por_id(
    id: int,
    service: UsuarioService = Depends(get_usuario_service),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
):
    usuario = service.get_usuario_por_id(id, usuario_logado)
    return usuario

@router.get(
    "/admins",
    response_model=list[UsuarioAdminResponse]
)
def listar_usuarios_admins(
    service: UsuarioService = Depends(get_usuario_service),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
):    
    admins = service.get_admins(usuario_logado)
    return admins

@router.post(
    "/admins",
    response_model=UsuarioAdminResponse
)
def criar_usuario_admin(
    usuario_data: UsuarioRequest,
    service: UsuarioService = Depends(get_usuario_service),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
):
    service.checar_usuario_is_admin(usuario_logado)

    usuario = Usuario.model_validate(usuario_data)
    usuario.is_admin = True
    novo_usuario = service.add_admin(usuario)
    return novo_usuario

@router.patch("/{id}")
def atualizar_usuario(
    id: int,
    usuario_data: UsuarioPatchRequest,
    service: UsuarioService = Depends(get_usuario_service),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
):
    usuario = service.update_usuario(id, usuario_data, usuario_logado)
    
    return {"detail": "Usuário atualizado com sucesso.", "usuario_id": usuario.id}

@router.delete("/{id}")
def deletar_usuario(
    id: int,
    service: UsuarioService = Depends(get_usuario_service),
    usuario_logado: Usuario = Depends(get_usuario_autenticado)
):
    service.delete_usuario(id, usuario_logado)
    return {"detail": "Usuário deletado com sucesso."}

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
    service: UsuarioService = Depends(get_usuario_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    usuario = auth_service.get_usuario_se_alterar_senha_for_permitido(
        username=username,
        pwd_reset_token=pwd_reset_token,
    )

    usuario_atualizado = service.update_senha_usuario(
        usuario,
        senha_data
    )

    return {"detail": "Senha alterada com sucesso.", "id": usuario_atualizado.id}