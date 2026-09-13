from app.domain.entities.estoque import Peca
from app.domain.exceptions import NotFoundException, ConflictException, BusinessRuleException


class GerenciarEstoqueUseCase:
    """Casos de uso do estoque de peças (CRUD + entrada de estoque)."""

    def __init__(self, estoque_repo):
        self._repo = estoque_repo

    def criar(self, dados: dict) -> Peca:
        if self._repo.existe_nome(dados["nome"]):
            raise ConflictException("Já existe uma peça com esse nome")
        peca = Peca(**dados)
        self._repo.adicionar(peca)
        self._repo.commit()
        self._repo.refresh(peca)
        return peca

    def listar(self, skip: int = 0, limit: int = 100) -> list[Peca]:
        return self._repo.listar(skip, limit)

    def obter(self, peca_id) -> Peca:
        peca = self._repo.buscar_peca(peca_id)
        if not peca:
            raise NotFoundException("Peça não encontrada")
        return peca

    def atualizar(self, peca_id, dados: dict) -> Peca:
        peca = self.obter(peca_id)
        if self._repo.existe_nome(dados["nome"], exclude_id=peca_id):
            raise ConflictException("Já existe uma peça com esse nome")
        for campo, valor in dados.items():
            setattr(peca, campo, valor)
        self._repo.commit()
        self._repo.refresh(peca)
        return peca

    def remover(self, peca_id) -> None:
        peca = self.obter(peca_id)
        if self._repo.possui_vinculo_os(peca_id):
            raise BusinessRuleException("Peça vinculada a OS ativa — não pode ser removida")
        self._repo.remover(peca)
        self._repo.commit()

    def registrar_entrada(self, peca_id, quantidade: int, motivo: str | None) -> Peca:
        peca = self.obter(peca_id)
        peca.quantidade += quantidade
        self._repo.registrar_movimentacao(peca_id, "ENTRADA", quantidade, motivo)
        self._repo.commit()
        self._repo.refresh(peca)
        return peca
