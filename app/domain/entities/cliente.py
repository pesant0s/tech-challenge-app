class Cliente:
    """Cliente da oficina (entidade de domínio pura, sem dependência de ORM)."""

    def __init__(self, nome=None, cpf_cnpj=None, telefone=None, email=None, ativo=True, id=None):
        self.id = id
        self.nome = nome
        self.cpf_cnpj = cpf_cnpj
        self.email = email
        self.telefone = telefone
        self.ativo = ativo


class Veiculo:
    """Veículo vinculado a um cliente (entidade de domínio pura)."""

    def __init__(self, placa=None, marca=None, modelo=None, ano=None, cliente_id=None, id=None):
        self.id = id
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.cliente_id = cliente_id
