from fastapi import FastAPI

from .routers import main_router

from task_manager_api.database import (
    create_db_and_tables,
    create_usuario_admin,
)

def lifespan(app: FastAPI):
    """Função de ciclo de vida da aplicação."""
    
    # Executa na inicialização da aplicação
    create_db_and_tables()
    create_usuario_admin()
    yield  # Separa a inicialização do encerramento
    # Executa no encerramento da aplicação
    pass

app = FastAPI(
    title="Gerenciador de Tarefas API",
    version="0.1.0",
    description="API para gerenciamento de tarefas, com autenticação e controle de acesso.",
    lifespan=lifespan
)

# Inclui as rotas no app
app.include_router(main_router)