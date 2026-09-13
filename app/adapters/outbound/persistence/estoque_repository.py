from sqlalchemy import func
from sqlalchemy.orm import Session
from app.domain.entities.estoque import Peca, MovimentacaoEstoque
from app.domain.entities.os import ItemOS
from app.domain.exceptions import NotFoundException, BusinessRuleException


class EstoqueRepositoryAdapter:
    """Implementação SQLAlchemy para operações de estoque de peças."""

    def __init__(self, db: Session):
        self._db = db

    def buscar_peca(self, peca_id) -> Peca | None:
        return self._db.query(Peca).filter(Peca.id == peca_id).first()

    def baixar_estoque(self, peca_id, quantidade: int, motivo: str = "Baixa por OS") -> None:
        # FOR UPDATE: duas OS não consomem a mesma peça entre a checagem e o commit.
        p = self._db.query(Peca).filter(Peca.id == peca_id).with_for_update().first()
        if not p:
            raise NotFoundException("Peça não encontrada")
        if p.quantidade < quantidade:
            raise BusinessRuleException(f"Estoque insuficiente para peça '{p.nome}'")
        p.quantidade -= quantidade
        self._db.add(MovimentacaoEstoque(peca_id=peca_id, tipo="SAIDA", quantidade=quantidade, motivo=motivo))
        self._db.flush()

    def listar(self, skip: int = 0, limit: int = 100) -> list[Peca]:
        return self._db.query(Peca).offset(skip).limit(limit).all()

    def existe_nome(self, nome: str, exclude_id=None) -> bool:
        q = self._db.query(Peca).filter(func.lower(Peca.nome) == nome.strip().lower())
        if exclude_id:
            q = q.filter(Peca.id != exclude_id)
        return q.first() is not None

    def possui_vinculo_os(self, peca_id) -> bool:
        return self._db.query(ItemOS).filter(ItemOS.peca_id == peca_id).first() is not None

    def registrar_movimentacao(self, peca_id, tipo: str, quantidade: int, motivo: str | None) -> None:
        self._db.add(MovimentacaoEstoque(peca_id=peca_id, tipo=tipo, quantidade=quantidade, motivo=motivo))

    def adicionar(self, peca) -> None:
        self._db.add(peca)

    def remover(self, peca) -> None:
        self._db.delete(peca)

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, peca) -> None:
        self._db.refresh(peca)
