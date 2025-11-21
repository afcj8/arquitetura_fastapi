from typing import Optional
from sqlmodel import Session
from fastapi import APIRouter, Depends
from task_manager_api.database import get_session
from fastapi import APIRouter, HTTPException, status
from task_manager_api.models.tarefa import Tarefa
from task_manager_api.dependencies import get_usuario_autenticado
from task_manager_api.repositories.tarefa_repository import TarefaRepository
from task_manager_api.services.tarefa_service import TarefaService
from task_manager_api.serializers.tarefa_serializer import (
    TarefaRequest, 
    TarefaResponse
)

router = APIRouter()

@router.get("",
    response_model=list[TarefaResponse]
)
def listar_tarefas(
    usuario: int = Depends(get_usuario_autenticado),
    session: Session = Depends(get_session)
):
    repo = TarefaRepository(session)
    service = TarefaService(repo)
    tarefas = service.get_tarefas_por_usuario_id(usuario.id)
    return tarefas

@router.post("",
    response_model=TarefaResponse,
    status_code=201
)
def criar_tarefa(
    tarefa_data: TarefaRequest,
    usuario: int = Depends(get_usuario_autenticado),
    session: Session = Depends(get_session)
):
    repo = TarefaRepository(session)
    service = TarefaService(repo)
    
    tarefa = Tarefa(
        **tarefa_data.model_dump(),
        usuario_id=usuario.id
    )
    
    nova_tarefa = service.add_tarefa(tarefa)
    return nova_tarefa