import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    ATENDENTE = "ATENDENTE"


class Usuario:
    """Usuário do sistema (entidade de domínio pura, sem dependência de ORM)."""

    def __init__(self, username=None, hashed_password=None, role=RoleEnum.ATENDENTE,
                 ativo=True, id=None):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.role = role
        self.ativo = ativo
