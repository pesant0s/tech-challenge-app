from app.application.eventos_os import registrar_mudanca_de_status
from app.domain.entities.os import OrdemDeServico
from app.domain.exceptions import BusinessRuleException
from app.domain.ports.os_repository import OSRepositoryPort
from app.domain.value_objects.documentos import CpfCnpj


class AprovarOSUseCase:
    """Cliente aprova o orçamento informando seu CPF/CNPJ."""

    def __init__(self, os_repo: OSRepositoryPort, cliente_repo):
        self._os_repo = os_repo
        self._cliente_repo = cliente_repo

    def executar(self, os_id, cpf_cnpj: str) -> OrdemDeServico:
        try:
            digits = CpfCnpj.from_str(cpf_cnpj).digits
        except ValueError as exc:
            raise BusinessRuleException(str(exc))

        os = self._os_repo.buscar_para_escrita(os_id)
        cliente = self._cliente_repo.buscar_por_cpf_cnpj_digits(digits)
        if not cliente or os.cliente_id != cliente.id:
            raise BusinessRuleException("CPF/CNPJ não corresponde ao titular desta OS")

        os.aprovar()
        self._os_repo.commit()
        self._os_repo.refresh(os)
        registrar_mudanca_de_status(os)
        return os
