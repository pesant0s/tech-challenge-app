from app.application.eventos_os import registrar_mudanca_de_status
from app.domain.entities.os import OrdemDeServico, ItemOS, StatusOS
from app.domain.exceptions import NotFoundException, BusinessRuleException
from app.domain.ports.email_port import EmailNotificacaoPort
from app.domain.ports.os_repository import OSRepositoryPort


class CriarOSUseCase:
    """Abre a OS com orçamento calculado e avisa o cliente pela porta de notificação."""

    def __init__(self, os_repo: OSRepositoryPort, catalogo_repo, estoque_repo, cliente_repo=None,
                 notificador: EmailNotificacaoPort | None = None):
        self._os_repo = os_repo
        self._catalogo = catalogo_repo
        self._estoque = estoque_repo
        self._cliente_repo = cliente_repo
        self._notificador = notificador

    def executar(self, cliente_id, veiculo_id, servicos, pecas) -> OrdemDeServico:
        itens = []
        for item in servicos:
            s = self._catalogo.buscar_servico(item.servico_id)
            if not s:
                raise NotFoundException(f"Serviço {item.servico_id} não encontrado")
            itens.append(ItemOS(servico_id=item.servico_id, quantidade=item.quantidade, preco_unitario=s.preco))
        for item in pecas:
            p = self._estoque.buscar_peca(item.peca_id)
            if not p:
                raise NotFoundException(f"Peça {item.peca_id} não encontrada")
            if p.quantidade < item.quantidade:
                raise BusinessRuleException(f"Estoque insuficiente para peça '{p.nome}'")
            itens.append(ItemOS(peca_id=item.peca_id, quantidade=item.quantidade, preco_unitario=p.preco))

        os = OrdemDeServico(cliente_id=cliente_id, veiculo_id=veiculo_id,
                            status=StatusOS.AGUARDANDO_APROVACAO, itens=itens)
        os.recalcular_total()
        self._os_repo.adicionar(os)
        self._os_repo.commit()
        self._os_repo.refresh(os)
        registrar_mudanca_de_status(os)

        if self._notificador:
            cliente = self._cliente_repo.buscar_por_id(cliente_id) if self._cliente_repo else None
            destinatario = (cliente.email or cliente.telefone) if cliente else "cliente"
            self._notificador.notificar_aprovacao_pendente(os.id, destinatario)
        return os
