from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from task_manager_api.dependencies import get_auth_service
from task_manager_api.services.auth_service import AuthService
from task_manager_api.serializers.token_serializer import TokenResponse, RefreshToken
from task_manager_api.services.token_service import criar_access_token, criar_refresh_token
from task_manager_api.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post(
    "/token",
    response_model=TokenResponse
)
def token(
    form: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    usuario = auth_service.autenticar_usuario(form.username, form.password)

    payload = {"sub": usuario.username}

    access_token = criar_access_token(payload)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = criar_refresh_token(payload, expires_delta=refresh_token_expires)

    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token, 
        token_type="bearer"
    )

@router.post(
    "/refresh-token",
    response_model=TokenResponse
)
def refresh_token(
    refresh_token_data: RefreshToken,
    auth_service: AuthService = Depends(get_auth_service)
):
    usuario = auth_service.refresh_token(refresh_token_data.refresh_token)

    access_token = criar_access_token(
        data={"sub": usuario.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        scope="refresh_token"
    )

    refresh_token = criar_refresh_token(
        data={"sub": usuario.username}
    )
    
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token, 
        token_type="bearer"
    )