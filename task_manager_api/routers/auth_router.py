from fastapi import APIRouter, Depends
from task_manager_api.database import get_session
from sqlmodel import Session
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.services.auth_service import AuthService
from task_manager_api.serializers.auth_serializer import AuthRequest
from task_manager_api.services.token_service import criar_access_token, criar_refresh_token

router = APIRouter()

@router.post("/login")
def login(form: AuthRequest, session: Session = Depends(get_session)):

    repo = UsuarioRepository(session)
    usuario_service = UsuarioService(repo)
    auth_service = AuthService(usuario_service)

    usuario = auth_service.autenticar_usuario(form.username, form.senha)

    payload = {"sub": usuario.username}

    access_token = criar_access_token(payload)
    refresh_token = criar_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }