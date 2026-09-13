from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ServicoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=200)
    descricao: str | None = Field(default=None, max_length=1000)
    preco: Decimal = Field(gt=0)
    tempo_estimado_minutos: int | None = Field(default=None, gt=0, le=2880)


class ServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    descricao: str | None = None
    preco: Decimal
    tempo_estimado_minutos: int | None = None
