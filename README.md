# Proposta de Arquitetura — `task_manager_api` (FastAPI)

> API de exemplo: **Sistema de Gerenciamento de Tarefas**  
> Demonstra boas práticas de arquitetura para FastAPI: separação por camadas, SRP, padrão DAO, Service Layer e Injeção de Dependências.

---

## Sumário

- Visão geral
- Estrutura de diretórios
- Principais conceitos arquiteturais
- Modelos (entidades)
- Endpoints (rotas) — resumo e exemplos
- Fluxo de requisição (ex.: router → service → repository)
- Autenticação e segurança
- Observações de comportamento (reset de senha, remoção em cascata)
- Vantagens / Desvantagens da arquitetura
- Manual do desenvolvedor (instalação, execução)

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
│ │ └── usuario_serailizer.py
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
| `usuario_id`   | int        | FK → users.id                           |
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

Request:

```json
{ "username": "admin", "password": "admin123" }
```

Response:

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
| GET    | `/usuarios/{id}`        | admin                    | Detalha os dados de um usuário específico. |
| GET    | `/usuarios/admins`      | admin                    | Retorna todos os usuários que são admins. |
| POST   | `/usuarios/admins`      | admin                    | Cria um usuário admin. |
| PATCH  | `/usuarios/{id}`        | apenas o próprio usuário | Atualiza um usuário. |
| DELETE | `/usuarios/{id}`        | admin                    | Deleta as tarefas em cascade. |
| POST   | `/usuarios/reset-senha` | pública                  | Gera um token de redefinição de senha (simulado via arquivo `email.log`). |
| PATCH  | `/usuarios/{username}/senha` | — (com token válido)  | Redefine a senha utilizando o token gerado. |

## 🛡️ Tarefas (`/tarefas`)

| Método | Rota                     | Permissão Necessária                     |
| ------ | ------------------------ | ---------------------------------------- |
| GET    | `/tarefas`               | autenticado — lista do usuário           |
| POST   | `/tarefas`               | autenticado — cria tarefa para o usuário |
| GET    | `/tarefas/{id}`          | autenticado — do usuário                 |
| PATCH  | `/tarefas/{id}`          | autenticado — do usuário                 |
| DELETE | `/tarefas/{id}`          | autenticado — do usuário                 |
| GET    | `/tarefas/usuarios/{id}` | admin — tarefas por usuário              |

## 📌 Observações

- O reset de senha envia o token para o arquivo `email.log`, simulando o envio por e-mail.
- Um usuário só consegue realizar o CRUD com as suas tarefas.
- Após deletar um usuário, todas as suas tarefas são deletadas também.

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