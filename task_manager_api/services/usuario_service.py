from task_manager_api.serializers.usuario_serializer import UsuarioPatchRequest, UsuarioSenhaPatchRequest
from task_manager_api.repositories.usuario_repository import UsuarioRepository
from task_manager_api.repositories.tarefa_repository import TarefaRepository
from task_manager_api.models.usuario import Usuario
from task_manager_api.security import criar_hash_senha
from fastapi.exceptions import HTTPException
from fastapi import status

class UsuarioService:
    def __init__(
        self, 
        usuario_repository: UsuarioRepository
    ):
        self.usuario_repository = usuario_repository

    def validar_username_senha(
        self, 
        usuario: Usuario
    ) -> None:
        if not usuario.username or not usuario.senha:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username e senha são obrigatórios")
        
    def checar_usuario_existente(
        self, 
        username: str, 
        email: str
    ) -> None:
        usuario_por_username = self.usuario_repository.get_usuario_por_username(username)
        if usuario_por_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username já cadastrado")
        
        usuario_por_email = self.usuario_repository.get_usuario_por_email(email)
        if usuario_por_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado")
        
    def checar_usuario_existente_excluindo_id(
        self, 
        username: str, 
        email: str, usuario_id: int
    ) -> None:
        usuario_por_username = self.usuario_repository.get_usuario_por_username_excluindo_id(username, usuario_id)
        if usuario_por_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username já cadastrado")
        
        usuario_por_email = self.usuario_repository.get_usuario_por_email_excluindo_id(email, usuario_id)
        if usuario_por_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado")
        
    def checar_usuario_is_admin(
        self,
        usuario: Usuario
    ) -> None:
        if not usuario.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ação permitida apenas para administradores."
            )
        
    def get_usuarios(
        self,
        usuario: Usuario
    ) -> list[Usuario]:
        self.checar_usuario_is_admin(usuario)
        usuarios = self.usuario_repository.get_usuarios()
        return usuarios
    
    def get_admins(
        self,
        usuario: Usuario
    ) -> list[Usuario]:
        self.checar_usuario_is_admin(usuario)
        admins = self.usuario_repository.get_admins()
        return admins
    
    def get_tarefas_por_usuario_id(
        self,
        usuario_id: int,
        usuario_logado: Usuario
    ) -> list[Usuario]:
        usuario = self.usuario_repository.get_usuario_por_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        self.checar_usuario_is_admin(usuario_logado)
        tarefa_repository = TarefaRepository(self.usuario_repository.db_session)
        tarefas = tarefa_repository.get_tarefas_por_usuario_id(usuario_id)
        return tarefas
        
    def add_usuario(
        self, 
        usuario: Usuario
    ) -> Usuario:
        self.validar_username_senha(usuario)
        self.checar_usuario_existente(usuario.username, usuario.email)
        usuario.senha = criar_hash_senha(usuario.senha)
        novo_usuario = self.usuario_repository.add_update_usuario(usuario)
        return novo_usuario
    
    def add_admin(
        self,
        usuario: Usuario
    ) -> Usuario:
        self.validar_username_senha(usuario)
        self.checar_usuario_existente(usuario.username, usuario.email)
        self.checar_usuario_is_admin(usuario)
        usuario.senha = criar_hash_senha(usuario.senha)
        usuario.is_admin = True
        novo_usuario =  self.usuario_repository.add_update_usuario(usuario)
        return novo_usuario
    
    def update_usuario(
        self,
        usuario_id: int,
        dados: UsuarioPatchRequest,
        usuario_logado: Usuario
    ) -> Usuario:

        usuario_existente = self.usuario_repository.get_usuario_por_id(usuario_id)

        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        if usuario_existente.id != usuario_logado.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para atualizar este usuário."
            )
        
        if dados.username is not None:
            self.checar_usuario_existente_excluindo_id(dados.username, usuario_existente.email, usuario_id)
            usuario_existente.username = dados.username

        if dados.email is not None:
            self.checar_usuario_existente_excluindo_id(usuario_existente.username, dados.email, usuario_id)
            usuario_existente.email = dados.email

        if dados.nome is not None:
            usuario_existente.nome = dados.nome

        return self.usuario_repository.add_update_usuario(usuario_existente)
    
    def update_senha_usuario(
        self,
        usuario: Usuario,
        dados: UsuarioSenhaPatchRequest,
    ) -> Usuario:
        
        if dados.senha != dados.confirmar_senha:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha e confirmar senha não coincidem."
            )

        usuario.senha = criar_hash_senha(dados.senha)
        
        return self.usuario_repository.add_update_usuario(usuario)
    
    def delete_usuario(
        self,
        usuario_id: int,
        usuario_logado: Usuario
    ) -> None:
        
        usuario_existente = self.usuario_repository.get_usuario_por_id(usuario_id)
        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        self.checar_usuario_is_admin(usuario_logado)
        self.usuario_repository.delete_usuario(usuario_existente)