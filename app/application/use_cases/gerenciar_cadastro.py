from app.domain.entities.cliente import Cliente, Veiculo
from app.domain.exceptions import NotFoundException, ConflictException, BusinessRuleException
from app.domain.value_objects.documentos import CpfCnpj


class GerenciarClientesUseCase:
    """Casos de uso de clientes (CRUD com regras de negócio)."""

    def __init__(self, cliente_repo):
        self._repo = cliente_repo

    def criar(self, dados: dict) -> Cliente:
        # `cpf_cnpj` já chega apenas com dígitos (validado pelo value object no schema).
        if self._repo.existe_cpf_cnpj(dados["cpf_cnpj"]):
            raise ConflictException("CPF/CNPJ já cadastrado")
        cliente = Cliente(**dados)
        self._repo.adicionar(cliente)
        self._repo.commit()
        self._repo.refresh(cliente)
        return cliente

    def listar(self, skip: int = 0, limit: int = 100) -> list[Cliente]:
        return self._repo.listar(skip, limit)

    def obter(self, cliente_id) -> Cliente:
        cliente = self._repo.buscar_por_id(cliente_id)
        if not cliente:
            raise NotFoundException("Cliente não encontrado")
        return cliente

    def buscar_por_documento(self, cpf_cnpj: str) -> Cliente:
        try:
            digits = CpfCnpj.from_str(cpf_cnpj).digits
        except ValueError as exc:
            raise BusinessRuleException(str(exc))
        cliente = self._repo.buscar_por_cpf_cnpj_digits(digits)
        if not cliente:
            raise NotFoundException("Cliente não encontrado")
        return cliente

    def atualizar(self, cliente_id, dados: dict) -> Cliente:
        cliente = self.obter(cliente_id)
        for campo, valor in dados.items():
            setattr(cliente, campo, valor)
        self._repo.commit()
        self._repo.refresh(cliente)
        return cliente


class GerenciarVeiculosUseCase:
    """Casos de uso de veículos, vinculados a um cliente existente."""

    def __init__(self, veiculo_repo, cliente_repo):
        self._repo = veiculo_repo
        self._cliente_repo = cliente_repo

    def _garantir_cliente(self, cliente_id) -> None:
        if not self._cliente_repo.buscar_por_id(cliente_id):
            raise NotFoundException("Cliente não encontrado")

    def criar(self, dados: dict) -> Veiculo:
        self._garantir_cliente(dados["cliente_id"])
        if self._repo.existe_placa(dados["placa"]):
            raise ConflictException("Placa já cadastrada")
        veiculo = Veiculo(**dados)
        self._repo.adicionar(veiculo)
        self._repo.commit()
        self._repo.refresh(veiculo)
        return veiculo

    def listar_por_cliente(self, cliente_id) -> list[Veiculo]:
        self._garantir_cliente(cliente_id)
        return self._repo.listar_por_cliente(cliente_id)

    def obter(self, veiculo_id) -> Veiculo:
        veiculo = self._repo.buscar_por_id(veiculo_id)
        if not veiculo:
            raise NotFoundException("Veículo não encontrado")
        return veiculo

    def atualizar(self, veiculo_id, dados: dict) -> Veiculo:
        veiculo = self.obter(veiculo_id)
        for campo, valor in dados.items():
            setattr(veiculo, campo, valor)
        self._repo.commit()
        self._repo.refresh(veiculo)
        return veiculo

    def remover(self, veiculo_id) -> None:
        veiculo = self.obter(veiculo_id)
        self._repo.remover(veiculo)
        self._repo.commit()
