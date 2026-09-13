from app.domain.entities.os import OrdemDeServico
from app.domain.ports.os_repository import OSRepositoryPort
from app.domain.value_objects.webhook import AcaoWebhook
from app.application.use_cases.aprovar_os import AprovarOSUseCase
from app.application.use_cases.rejeitar_os import RejeitarOSUseCase


class ProcessarWebhookEmailUseCase:
    """Processa a resposta do cliente recebida via link de e-mail."""

    def __init__(self, os_repo: OSRepositoryPort, cliente_repo):
        self._os_repo = os_repo
        self._cliente_repo = cliente_repo

    def executar(self, os_id, acao: AcaoWebhook, cpf_cnpj: str) -> OrdemDeServico:
        caso_de_uso = AprovarOSUseCase if acao == AcaoWebhook.APROVAR else RejeitarOSUseCase
        return caso_de_uso(os_repo=self._os_repo, cliente_repo=self._cliente_repo).executar(os_id, cpf_cnpj)
