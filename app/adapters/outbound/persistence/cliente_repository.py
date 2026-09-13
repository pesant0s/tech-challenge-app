from sqlalchemy.orm import Session
from app.domain.entities.cliente import Cliente, Veiculo


class ClienteRepositoryAdapter:
    """Implementação SQLAlchemy do repositório de clientes."""

    def __init__(self, db: Session):
        self._db = db

    def buscar_por_cpf_cnpj_digits(self, digits: str) -> Cliente | None:
        return self._db.query(Cliente).filter(Cliente.cpf_cnpj == digits).first()

    def buscar_por_id(self, cliente_id) -> Cliente | None:
        return self._db.query(Cliente).filter(Cliente.id == cliente_id).first()

    def existe_cpf_cnpj(self, digits: str) -> bool:
        return self.buscar_por_cpf_cnpj_digits(digits) is not None

    def listar(self, skip: int = 0, limit: int = 100) -> list[Cliente]:
        return self._db.query(Cliente).offset(skip).limit(limit).all()

    def adicionar(self, cliente) -> None:
        self._db.add(cliente)

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, cliente) -> None:
        self._db.refresh(cliente)


class VeiculoRepositoryAdapter:
    """Implementação SQLAlchemy do repositório de veículos."""

    def __init__(self, db: Session):
        self._db = db

    def buscar_por_id(self, veiculo_id) -> Veiculo | None:
        return self._db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()

    def existe_placa(self, placa: str) -> bool:
        return self._db.query(Veiculo).filter(Veiculo.placa == placa).first() is not None

    def listar_por_cliente(self, cliente_id) -> list[Veiculo]:
        return self._db.query(Veiculo).filter(Veiculo.cliente_id == cliente_id).all()

    def adicionar(self, veiculo) -> None:
        self._db.add(veiculo)

    def remover(self, veiculo) -> None:
        self._db.delete(veiculo)

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, veiculo) -> None:
        self._db.refresh(veiculo)
