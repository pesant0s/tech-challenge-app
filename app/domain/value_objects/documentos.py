import re
from dataclasses import dataclass
from typing import Annotated
from pydantic import BeforeValidator

PESOS_CNPJ = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def _digito(base: str, pesos) -> str:
    resto = sum(int(d) * p for d, p in zip(base, pesos)) % 11
    return "0" if resto < 2 else str(11 - resto)


@dataclass(frozen=True)
class CpfCnpj:
    """Value Object: CPF (11 dígitos) ou CNPJ (14 dígitos). Armazena apenas dígitos."""

    digits: str

    def __post_init__(self):
        if not self.digits.isdigit() or len(self.digits) not in (11, 14):
            raise ValueError(f"CpfCnpj inválido: '{self.digits}'")

    @classmethod
    def from_str(cls, value: str) -> "CpfCnpj":
        if not re.match(r"^[\d.\-/]+$", value):
            raise ValueError(
                "CPF/CNPJ contém caracteres inválidos — use apenas dígitos e pontuação padrão (., -, /)"
            )
        d = re.sub(r"\D", "", value)
        if len(d) == 11:
            tipo, pesos = "CPF", (range(10, 1, -1), range(11, 1, -1))
        elif len(d) == 14:
            tipo, pesos = "CNPJ", (PESOS_CNPJ, [6] + PESOS_CNPJ)
        else:
            raise ValueError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")
        if len(set(d)) == 1 or d[-2:] != _digito(d[:-2], pesos[0]) + _digito(d[:-1], pesos[1]):
            raise ValueError(f"{tipo} inválido — dígitos verificadores incorretos")
        return cls(digits=d)


@dataclass(frozen=True)
class Placa:
    """Value Object: placa no padrão antigo (AAA-1234) ou Mercosul (AAA1A23)."""

    valor: str

    @classmethod
    def from_str(cls, value: str) -> "Placa":
        v = value.upper().strip()
        if not re.match(r"^[A-Z]{3}(-\d{4}|\d[A-Z]\d{2})$", v):
            raise ValueError("Placa inválida. Formatos aceitos: AAA-1234 (antigo) ou AAA1A23 (Mercosul)")
        return cls(valor=v)


CpfCnpjStr = Annotated[str, BeforeValidator(lambda v: CpfCnpj.from_str(str(v)).digits)]
PlacaStr = Annotated[str, BeforeValidator(lambda v: Placa.from_str(str(v)).valor)]
