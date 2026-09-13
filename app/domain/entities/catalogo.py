class Servico:
    """Serviço ofertado pela oficina (entidade de domínio pura, sem ORM)."""

    def __init__(self, nome=None, preco=None, descricao=None,
                 tempo_estimado_minutos=None, id=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.tempo_estimado_minutos = tempo_estimado_minutos
