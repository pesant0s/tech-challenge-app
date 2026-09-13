from typing import Protocol
from uuid import UUID


class EmailNotificacaoPort(Protocol):
    """Notificação ao cliente, sem acoplar o domínio ao meio de entrega."""

    def notificar_aprovacao_pendente(self, os_id: UUID, destinatario: str) -> None: ...
