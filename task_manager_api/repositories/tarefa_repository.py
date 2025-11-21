"""Repositório para operações relacionadas à tarefa."""

from task_manager_api.models.tarefa import Tarefa
from sqlmodel import Session, select

class TarefaRepository:    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_tarefas_por_usuario_id(self, usuario_id: int) -> list[Tarefa]:
        tarefas = self.db_session.exec(select(Tarefa).where(Tarefa.usuario_id == usuario_id)).all()
        return tarefas
    
    def get_tarefa_por_id(self, tarefa_id: int) -> Tarefa | None:
        tarefa = self.db_session.get(Tarefa, tarefa_id)
        return tarefa

    def add_update_tarefa(self, tarefa: Tarefa) -> Tarefa:
        self.db_session.add(tarefa)
        self.db_session.commit()
        self.db_session.refresh(tarefa)
        return tarefa
    
    def delete_tarefa(self, tarefa: Tarefa) -> None:
        self.db_session.delete(tarefa)
        self.db_session.commit()