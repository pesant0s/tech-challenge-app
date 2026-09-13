from app.domain.entities.os import OrdemDeServico
from app.domain.exceptions import NotFoundException
from app.domain.ports.os_repository import OSRepositoryPort


class ObterOSUseCase:
    """Consulta uma OS; para um cliente, a OS de outro responde como inexistente."""

    def __init__(self, os_repo: OSRepositoryPort):
        self._os_repo = os_repo

    def executar(self, os_id, cliente_id=None) -> OrdemDeServico:
        os = self._os_repo.buscar_por_id(os_id)
        if os is None or (cliente_id is not None and os.cliente_id != cliente_id):
            raise NotFoundException("Ordem de Serviço não encontrada")
        return os
