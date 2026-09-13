class Peca:
    """Peça/insumo em estoque (entidade de domínio pura, sem ORM)."""

    def __init__(self, nome=None, preco=None, descricao=None,
                 quantidade=0, estoque_minimo=1, id=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.quantidade = quantidade
        self.estoque_minimo = estoque_minimo


class MovimentacaoEstoque:
    """Registro de entrada/saída de estoque (entidade de domínio pura)."""

    def __init__(self, peca_id=None, tipo=None, quantidade=None, motivo=None, id=None):
        self.id = id
        self.peca_id = peca_id
        self.tipo = tipo  # ENTRADA | SAIDA
        self.quantidade = quantidade
        self.motivo = motivo
