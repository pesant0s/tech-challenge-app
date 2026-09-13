import logging
from uuid import UUID

logger = logging.getLogger("oficina.notificacoes")


class EmailSimuladoAdapter:
    """Implementa EmailNotificacaoPort registrando o e-mail em log, sem provedor real."""

    def notificar_aprovacao_pendente(self, os_id: UUID, destinatario: str) -> None:
        logger.info(
            "📧 [E-MAIL SIMULADO] Para: %s | Assunto: Aprovação da OS %s | "
            "Corpo: Sua ordem de serviço está aguardando aprovação. "
            "Responda APROVAR ou REJEITAR pelo link do e-mail.",
            destinatario, os_id,
        )
