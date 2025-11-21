from fastapi import APIRouter, Depends
from task_manager_api.models.tarefa import Tarefa
from task_manager_api.dependencies import get_usuario_autenticado, get_tarefa_service
from task_manager_api.services.tarefa_service import TarefaService
from task_manager_api.serializers.tarefa_serializer import (
    TarefaRequest, 
    TarefaResponse,
    TarefaPatchRequest
)

router = APIRouter()

@router.get("",
    response_model=list[TarefaResponse]
)
def listar_tarefas(
    usuario: int = Depends(get_usuario_autenticado),
    service: TarefaService = Depends(get_tarefa_service)
):
    return service.get_tarefas_por_usuario_id(usuario.id)

@router.post("",
    response_model=TarefaResponse,
    status_code=201
)
def criar_tarefa(
    tarefa_data: TarefaRequest,
    usuario: int = Depends(get_usuario_autenticado),
    service: TarefaService = Depends(get_tarefa_service)
):
    tarefa = Tarefa(
        **tarefa_data.model_dump(),
        usuario_id=usuario.id
    )

    nova_tarefa = service.add_tarefa(tarefa)
    return nova_tarefa

@router.get(
    "/{id}",
    response_model=TarefaResponse
)
def obter_tarefa(
    id: int,
    usuario: int = Depends(get_usuario_autenticado),
    service: TarefaService = Depends(get_tarefa_service)
):
    tarefa = service.get_tarefa_por_id(id, usuario.id)
    return tarefa

@router.patch(
    "/{id}",
    response_model=TarefaResponse
)
def atualizar_tarefa(
    id: int,
    tarefa_data: TarefaPatchRequest,
    usuario: int = Depends(get_usuario_autenticado),
    service: TarefaService = Depends(get_tarefa_service)
):
    tarefa = service.update_tarefa(id, tarefa_data, usuario.id)
    return tarefa

@router.delete(
    "/{id}",
    status_code=200
)
def deletar_tarefa(
    id: int,
    usuario: int = Depends(get_usuario_autenticado),
    service: TarefaService = Depends(get_tarefa_service)
):
    service.delete_tarefa(id, usuario.id)
    return {"detail": "Tarefa deletada com sucesso."}