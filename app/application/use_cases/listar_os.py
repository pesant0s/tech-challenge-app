from app.domain.entities.os import OrdemDeServico, StatusOS
from app.domain.ports.os_repository import OSRepositoryPort


class ListarOSUseCase:
    """Retorna a lista de OS com filtro opcional de status."""

    def __init__(self, os_repo: OSRepositoryPort):
        self._os_repo = os_repo

    def executar(self, skip: int = 0, limit: int = 100, status: StatusOS | None = None) -> list[OrdemDeServico]:
        return self._os_repo.listar(skip, limit, status)
