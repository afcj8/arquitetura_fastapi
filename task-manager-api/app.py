from fastapi import FastAPI

app = FastAPI(
    title="Gerenciador de Tarefas API",
    version="0.1.0",
    description="API para gerenciamento de tarefas, com autenticação e controle de acesso.",
)