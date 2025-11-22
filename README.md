# Proposta de Arquitetura — `task_manager_api` (FastAPI)

> API de exemplo: **Sistema de Gerenciamento de Tarefas**  
> Demonstra boas práticas de arquitetura para FastAPI: separação por camadas, SRP, padrão DAO, Service Layer e Injeção de Dependências.

## Visão geral

`task_manager_api` é uma API construída com **FastAPI**, **SQLAlchemy** e **SQLite**, que exemplifica como estruturar uma aplicação em camadas para torná-la testável, escalável e fácil de manter. A API permite o gerenciamento de **usuários** e **tarefas**, com controle de acesso via **JWT**.

Ao rodar a aplicação pela primeira vez, se o banco não existir, ele é criado (`database.db`) e um usuário administrador padrão é inserido:

- **Usuário:** `admin`
- **Senha:** `admin123`

## Estrutura de diretórios

```
task_manager_api/
│ ├── models/
| | ├── __init__.py
│ │ ├── tarefa.py
│ │ └── usuario.py
│ ├── repositories/
│ │ ├── tarefa_repository.py
│ │ └── usuario_repository.py
│ ├── routers/
│ │ ├── __init__.py
│ │ ├── auth_router.py
│ │ ├── tarefa_router.py
│ │ └── usuario_router.py
│ ├── serializers/
│ │ ├── tarefa_serializer.py
│ │ ├── token_serializer.py
│ │ └── usuario_serializer.py
│ ├── services/
│ │ ├── auth_service.py
│ │ ├── reset_senha_service.py
│ │ ├── tarefa_service.py
│ │ ├── token_service.py
│ │ └── usuario_service.py
│ ├── __init__.py
│ ├── app.py
│ ├── config.py
│ ├── database.py
│ ├── dependencies.py
│ └── security.py
├── .gitignore 
├── README.md
└── requirements.txt
```

## Conceitos arquiteturais (resumo)

- **SRP (Single Responsibility Principle)**: cada módulo tem responsabilidade única.
- **DAO / Repositories**: camada responsável pelo acesso ao banco.
- **Service Layer**: regras de negócio, validações e coordenação de repositories.
- **Serializers (Pydantic)**: validação/serialização de entrada e saída.
- **Routers**: expõem endpoints HTTP.
- **Dependencies / DI**: injeção de dependências (`Depends`).

**Fluxo de uma requisição**

Requisição: `serializer (request) → router → service → repository → models`  
Resposta: `serializer (response) ← router ← service ← repository ← models`

## Modelos (entidades)

### Usuário

| Atributo       | Tipo       | Observações          |
|----------------|------------|----------------------|
| `id`           | int        | PK                   |
| `username`     | str        | único                |
| `nome`         | str        | obrigatório          |
| `senha`        | str        | hash                 |
| `email`        | str        | único                |
| `is_admin`     | bool       | flag admin           |
| `data_criacao` | datetime   | automático           |

### Tarefa

| Atributo       | Tipo       | Observações                             |
|----------------|------------|-----------------------------------------|
| `id`           | int        | PK                                      |
| `usuario_id`   | int        | FK → usuario.id                           |
| `titulo`       | str        | obrigatório                             |
| `descricao`    | str        | opcional                                |
| `status`       | enum       | pendente/em_progresso/concluida         |
| `prioridade`   | enum       | baixa/media/alta                        |
| `data_criacao` | datetime   | automático                              |

## Endpoints (resumo)

> Todas as rotas retornam JSON. Detalhes finais aparecem na documentação gerada (Swagger/Redoc).

## 🔐 Autenticação

### `POST /token`

Troca `username` + `senha` por **access token** + **refresh token**.

Exemplo (request):

```json
{ "username": "admin", "password": "admin123" }
```

Exemplo (response):

```
{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

### `POST /refresh-token`

Recebe refresh token e retorna um novo access token.

## 👤 Usuários (`/usuarios`)

| Método | Rota                    | Permissão Necessária     | Descrição |
| ------ | ----------------------- |------------------------- | --------- |
| GET    | `/usuarios`             | admin                    | Lista todos os usuários. |
| POST   | `/usuarios`             | pública (registro)       | Cria um novo usuário. |
| GET    | `/usuarios/me`          | autenticado              | Retorna os dados do usuário autenticado. |
| GET    | `/usuarios/{id}`        | autenticado              | Exibe dados de um usuário. Admin vê qualquer um; usuário comum só a si mesmo. |
| GET    | `/usuarios/admins`      | admin                    | Retorna todos os usuários que são admins. |
| POST   | `/usuarios/admins`      | admin                    | Cria um usuário admin. |
| PATCH  | `/usuarios/{id}`        | autenticado              | Atualiza um usuário (apenas ele próprio). |
| DELETE | `/usuarios/{id}`        | admin                    | Deleta as tarefas em cascade. |
| POST   | `/usuarios/reset-senha` | pública                  | Gera um token de redefinição de senha (simulado via arquivo `email.log`). |
| PATCH  | `/usuarios/{username}/senha` | — (com token válido)| Redefine a senha utilizando o token gerado. |

## 📝 Tarefas (`/tarefas`)

| Método | Rota                     | Permissão Necessária                     |
| ------ | ------------------------ | ---------------------------------------- |
| GET    | `/tarefas`               | autenticado — lista do usuário           |
| POST   | `/tarefas`               | autenticado — cria tarefa para o usuário |
| GET    | `/tarefas/{id}`          | autenticado (próprias tarefas)           |
| PATCH  | `/tarefas/{id}`          | autenticado (próprias tarefas)           |
| DELETE | `/tarefas/{id}`          | autenticado (próprias tarefas)           |
| GET    | `/tarefas/usuarios/{id}` | admin — tarefas por usuário              |

## 📌 Observações

- O reset de senha envia o token para o arquivo `email.log`, simulando o envio por e-mail.
- Cada usuário só pode manipular suas próprias tarefas.
- Ao deletar um usuário, suas tarefas são removidas automaticamente (cascade).

## 👨🏻‍💻 Exemplo de uso da Arquitetura proposta

O exemplo a seguir demonstra o fluxo completo para **adicionar** e **deletar** uma tarefa pertencente a um usuário.
A operação envolve três camadas princípais da arquitetura: **repositório**, **serviço** e **rotas**.

## 📚 Repositório (`TarefaRepository`)

O repositório é responsável exclusivamente pelo acesso ao banco de dados e pelas operações CRUD da entidade `Tarefa`:

```
from task_manager_api.models.tarefa import Tarefa
from sqlmodel import Session

class TarefaRepository:    
    def __init__(self, db_session: Session):
        self.db_session = db_session

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
```

## 🧠 Serviços (`TarefaService`)

A camada de serviços implementa a lógica de negócios: validação, regras, permissões e coordenação entre camadas.

```
from task_manager_api.repositories.tarefa_repository import TarefaRepository
from task_manager_api.models.tarefa import Tarefa
from fastapi.exceptions import HTTPException
from fastapi import status

class TarefaService:
    def __init__(
        self, 
        tarefa_repository: TarefaRepository
    ):
        self.tarefa_repository = tarefa_repository
    
    def add_tarefa(
        self, 
        tarefa: Tarefa
    ) -> Tarefa:
        nova_tarefa = self.tarefa_repository.add_update_tarefa(tarefa)
        return nova_tarefa
    
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
```

## 🌐 Rotas (Routers)

As rotas recebem a requisição, validam dados via serializers e delegam a execução para a camada de serviços.

```
from fastapi import APIRouter, Depends
from task_manager_api.models.tarefa import Tarefa
from task_manager_api.dependencies import (
    get_usuario_autenticado,
    get_tarefa_service
)
from task_manager_api.services.tarefa_service import TarefaService
from task_manager_api.serializers.tarefa_serializer import (
    TarefaRequest, 
    TarefaResponse
)

router = APIRouter()

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
```

## 🔁 Serializer

A camada de serializer é responsável por definir como os dados devem ser enviados e recebidos pela API.
Ela garante que o formato das informações esteja correto tanto ao criar uma tarefa quanto ao retornar uma resposta.

```
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class TarefaRequest(BaseModel):
    """Representa o modelo de criação da tarefa"""
    
    titulo: str
    descricao: Optional[str] = None
    status: str
    prioridade: str
    data_criacao: Optional[datetime] = datetime.now()

class TarefaResponse(BaseModel):
    """Representa o modelo de resposta da tarefa"""
    
    id: int
    titulo: str
    descricao: Optional[str] = None
    status: str
    prioridade: str
    usuario_id: int
    data_criacao: datetime
```


## 🔗 Injeção de Dependências

As dependências são responsáveis por construir e entregar instâncias de repositórios, serviços e autenticação para as rotas, mantendo baixo acoplamento entre as camadas.

```
from fastapi import Depends
from sqlmodel import Session
from fastapi.security import OAuth2PasswordBearer
from task_manager_api.database import get_session
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.repositories.tarefa_repository import TarefaRepository
from task_manager_api.services.usuario_service import UsuarioService
from task_manager_api.services.tarefa_service import TarefaService
from task_manager_api.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_usuario_repository(
    session: Session = Depends(get_session)
):
    return UsuarioRepository(session)

def get_usuario_service(
    session=Depends(get_usuario_repository)
):
    return UsuarioService(session)

def get_auth_service(usuario_service=Depends(get_usuario_service)):
    return AuthService(usuario_service)

def get_tarefa_repository(
    session: Session = Depends(get_session)
):
    return TarefaRepository(session)

def get_tarefa_service(
    repo: TarefaRepository = Depends(get_tarefa_repository)
):
    return TarefaService(repo)

def get_usuario_autenticado(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.validar_token(token)
```

Ao aplicar o Princípio da Responsabilidade Única (SRP) em uma aplicação FastAPI, código não se torna apenas mais limpo e fácil de manter, mas também estabelece uma base sólida para a expansão futura da aplicação.

## DAO

- **Encapsulamento de Acesso a Dados:** O DAO fornece uma camada dedicada para gerenciar todas as operações de acesso a dados. Isso significa que qualquer alteração na lógica de persistência (por exemplo, a mudança de SQL para NoSQL) é realizada apenas na camada do DAO, sem afetar o restante da aplicação.
- **Reutilização:** A implementação do DAO pode ser reutilizada por diferentes serviços ou componentes que precisam interagir com dados da mesma entidade, eliminando a duplicação de código.
- **Testes simplificados:** Ao separar o acesso aos dados em sua própria camada, fica fácil criar mocks ou stubs para testes unitários, permitindo que a lógica de negócios seja testada isoladamente, sem depender do banco de dados real.
- **Facilidade de manutenção:** As operações de acesso a dados são centralizadas em uma classe DAO, facilitando a localização e correção de erros relacionados à persistência.

## Camada de Serviços

Ao separar a lógica de negócios em uma camada de serviços, obtém-se um código mais modular, mais fácil de manter e testar. Além disso, facilita a reutilização da lógica de negócios em diferentes contextos de aplicação.

## ⚖️ Vantagens e Desvantagens

### Vantagens
- separação clara de responsabilidades
- testabilidade elevada
- maior flexibilidade
- reuso de lógica
- escalabilidade por domínio

### Desvantagens
- mais arquivos / complexidade inicial
- transações em múltiplos repositórios exigem cuidado
- Serviços mal projetados tendem a acumular regras, verificações e fluxos, tornando-se componentes grandes e difíceis de testar ou evoluir.

## 🎯 Conclusão

Essa arquitetura:
- segue boas práticas recomendadas pela comunidade
- é alinhada ao SRP, SOLID e padrões de camadas
- favorece testes, escalabilidade e manutenção
- organiza o código por domínio e por responsabilidade
- deixa qualquer aplicação preparado para crescer com cada camada independente. 

## 🛠️ Manual do Desenvolvedor

1. Clone o repositório:
   ```bash
   git clone https://github.com/afcj8/arquitetura_fastapi.git
   ```

2. Verifique se o Python está instalado em sua máquina:
   ```bash
   python --version
   ```

3. Navegue até o diretório clonado:
   ```bash
   cd arquitetura_fastapi
   ```

4. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   ```

5. Ative o ambiente virtual:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

6. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

7. Execute a aplicação com o Uvicorn:
   ```bash
   uvicorn task_manager_api.app:app --reload
   ```

8. Acesse a documentação (Swagger UI) no navegador com a seguinte URL:
   ```bash
   http://localhost:8000/docs
   ```