from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.domain.entities.usuario import RoleEnum


class UsuarioCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    role: RoleEnum = RoleEnum.ATENDENTE


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    role: RoleEnum
    ativo: bool
