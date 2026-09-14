import enum
from datetime import datetime, timezone
from decimal import Decimal

from app.domain.exceptions import BusinessRuleException


class StatusOS(str, enum.Enum):
    AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO"
    RECEBIDA = "RECEBIDA"
    EM_DIAGNOSTICO = "EM_DIAGNOSTICO"
    EM_EXECUCAO = "EM_EXECUCAO"
    FINALIZADA = "FINALIZADA"
    ENTREGUE = "ENTREGUE"
    NEGADA = "NEGADA"
    ABANDONADA = "ABANDONADA"


class ItemOS:
    """Item de uma Ordem de Serviço (um serviço OU uma peça). Entidade pura."""

    def __init__(self, quantidade=1, preco_unitario=None, servico_id=None,
                 peca_id=None, os_id=None, id=None):
        self.id = id
        self.os_id = os_id
        self.servico_id = servico_id
        self.peca_id = peca_id
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario

    def calcular_subtotal(self) -> Decimal:
        return Decimal(str(self.preco_unitario)) * self.quantidade


class HistoricoStatusOS:
    """Entrada da OS em um status; a diferença entre entradas dá o tempo em cada status."""

    def __init__(self, status=None, entrou_em=None, os_id=None, id=None):
        self.id = id
        self.os_id = os_id
        self.status = status
        self.entrou_em = entrou_em


class OrdemDeServico:
    """Ordem de Serviço com máquina de estados de negócio. Entidade de domínio pura."""

    TRANSICOES_VALIDAS: dict[StatusOS, list[StatusOS]] = {
        StatusOS.AGUARDANDO_APROVACAO: [StatusOS.RECEBIDA, StatusOS.NEGADA, StatusOS.ABANDONADA],
        StatusOS.RECEBIDA:             [StatusOS.EM_DIAGNOSTICO],
        StatusOS.EM_DIAGNOSTICO:       [StatusOS.AGUARDANDO_APROVACAO, StatusOS.EM_EXECUCAO],
        StatusOS.EM_EXECUCAO:          [StatusOS.FINALIZADA],
        StatusOS.FINALIZADA:           [StatusOS.ENTREGUE],
        StatusOS.NEGADA:               [],
        StatusOS.ENTREGUE:             [],
        StatusOS.ABANDONADA:           [],
    }

    def __init__(self, cliente_id=None, veiculo_id=None, status=StatusOS.AGUARDANDO_APROVACAO,
                 valor_total=None, criado_em=None, iniciado_em=None, finalizado_em=None,
                 itens=None, historico=None, id=None):
        self.id = id
        self.cliente_id = cliente_id
        self.veiculo_id = veiculo_id
        self.status = status
        self.valor_total = valor_total
        self.criado_em = criado_em
        self.iniciado_em = iniciado_em
        self.finalizado_em = finalizado_em
        # Ao carregar do banco o ORM não chama __init__, então as coleções não são sobrescritas.
        self.itens = itens if itens is not None else []
        self.historico = historico if historico is not None else [HistoricoStatusOS(status, datetime.now(timezone.utc))]

    def transicionar_para(self, novo_status: StatusOS) -> None:
        permitidos = self.TRANSICOES_VALIDAS.get(self.status, [])
        if novo_status not in permitidos:
            raise BusinessRuleException(
                f"Transição inválida: {self.status} → {novo_status}. "
                f"Permitidos: {[s.value for s in permitidos]}"
            )
        agora = datetime.now(timezone.utc)
        self.status = novo_status
        self.historico.append(HistoricoStatusOS(novo_status, agora))
        if novo_status == StatusOS.EM_EXECUCAO:
            self.iniciado_em = agora
        if novo_status == StatusOS.FINALIZADA:
            self.finalizado_em = agora

    def aprovar(self) -> None:
        if self.status != StatusOS.AGUARDANDO_APROVACAO:
            raise BusinessRuleException(
                f"OS não está aguardando aprovação (status atual: {self.status})"
            )
        self.transicionar_para(StatusOS.RECEBIDA)

    def rejeitar(self) -> None:
        if self.status != StatusOS.AGUARDANDO_APROVACAO:
            raise BusinessRuleException(
                f"OS não está aguardando aprovação (status atual: {self.status})"
            )
        self.transicionar_para(StatusOS.NEGADA)

    def recalcular_total(self) -> None:
        self.valor_total = sum(item.calcular_subtotal() for item in self.itens)
