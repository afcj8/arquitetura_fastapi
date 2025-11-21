from fastapi import APIRouter

from .auth_router import router as auth_router
from .usuario_router import router as usuario_router
from .tarefa_router import router as tarefa_router

main_router = APIRouter()

main_router.include_router(auth_router, tags=["auth"])
main_router.include_router(usuario_router, prefix="/usuarios", tags=["usuarios"])
main_router.include_router(tarefa_router, prefix="/tarefas", tags=["tarefas"])