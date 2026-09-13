import re
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, EmailStr
from app.domain.value_objects.documentos import CpfCnpjStr, PlacaStr


def _normalizar_telefone(v: str) -> str:
    if not re.match(r"^[\d\s()\-+]+$", v):
        raise ValueError("Telefone contém caracteres inválidos")
    return re.sub(r"\D", "", v)


class ClienteCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    cpf_cnpj: CpfCnpjStr
    email: EmailStr | None = None
    telefone: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "João Silva",
                    "cpf_cnpj": "529.982.247-25",
                    "email": "joao@email.com",
                    "telefone": "(11) 99999-9999",
                }
            ]
        }
    }

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        digits = _normalizar_telefone(v)
        if not (10 <= len(digits) <= 11):
            raise ValueError("Telefone inválido — informe DDD + número (10 ou 11 dígitos)")
        return digits


class ClienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    telefone: str | None = None

    @model_validator(mode="before")
    @classmethod
    def rejeitar_cpf_cnpj(cls, data):
        if isinstance(data, dict) and "cpf_cnpj" in data:
            raise ValueError("CPF/CNPJ não pode ser alterado após o cadastro")
        return data

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = _normalizar_telefone(v)
        if not (10 <= len(digits) <= 11):
            raise ValueError("Telefone inválido — informe DDD + número (10 ou 11 dígitos)")
        return digits


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    cpf_cnpj: str
    email: str | None = None
    telefone: str
    ativo: bool = True


class VeiculoCreate(BaseModel):
    placa: PlacaStr
    marca: str = Field(min_length=1, max_length=100)
    modelo: str = Field(min_length=1, max_length=100)
    ano: str
    cliente_id: UUID

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "placa": "ABC-1234",
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "ano": "2022",
                    "cliente_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ]
        }
    }

    @field_validator("ano")
    @classmethod
    def validate_ano(cls, v: str) -> str:
        if not re.match(r"^\d{4}$", v) or not (1900 <= int(v) <= 2100):
            raise ValueError("Ano inválido")
        return v


class VeiculoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    placa: str
    marca: str
    modelo: str
    ano: str
    cliente_id: UUID
