from task_manager_api.repositories.tarefa_repository import TarefaRepository
from task_manager_api.serializers.tarefa_serializer import TarefaPatchRequest
from task_manager_api.models.tarefa import Tarefa
from fastapi.exceptions import HTTPException
from fastapi import status

class TarefaService:
    def __init__(
        self, 
        tarefa_repository: TarefaRepository
    ):
        self.tarefa_repository = tarefa_repository

    def get_tarefas_por_usuario_id(
        self, 
        usuario_id: int
    ) -> list[Tarefa]:
        tarefas = self.tarefa_repository.get_tarefas_por_usuario_id(usuario_id)
        return tarefas
    
    def get_tarefa_por_id(
        self, 
        tarefa_id: int,
        usuario_id: int
    ) -> Tarefa:
        tarefa = self.tarefa_repository.get_tarefa_por_id(tarefa_id)
        if not tarefa:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
        
        if tarefa.usuario_id != usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para acessar esta tarefa")
        
        return tarefa
    
    def add_tarefa(
        self, 
        tarefa: Tarefa
    ) -> Tarefa:
        nova_tarefa = self.tarefa_repository.add_update_tarefa(tarefa)
        return nova_tarefa
    
    def update_tarefa(
        self, 
        tarefa_id: int,
        dados: TarefaPatchRequest,
        usuario_id: int
    ) -> Tarefa:
        tarefa_existente = self.tarefa_repository.get_tarefa_por_id(tarefa_id)
        if not tarefa_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
        
        if tarefa_existente.usuario_id != usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para atualizar esta tarefa")
        
        if dados.titulo is not None:
            tarefa_existente.titulo = dados.titulo

        if dados.descricao is not None:
            tarefa_existente.descricao = dados.descricao

        if dados.status is not None:
            tarefa_existente.status = dados.status

        if dados.prioridade is not None:
            tarefa_existente.prioridade = dados.prioridade
        
        tarefa_atualizada = self.tarefa_repository.add_update_tarefa(tarefa_existente)
        return tarefa_atualizada
    
    def delete_tarefa(
        self, 
        tarefa_id: int,
        usuario_id: int
    ) -> None:
        tarefa_existente = self.tarefa_repository.get_tarefa_por_id(tarefa_id)
        if not tarefa_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
        
        if tarefa_existente.usuario_id != usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para deletar esta tarefa")
        
        self.tarefa_repository.delete_tarefa(tarefa_existente)