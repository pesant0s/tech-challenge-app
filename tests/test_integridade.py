"""Restrições CHECK: o banco recusa o que a API já não deixaria passar."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


@pytest.mark.parametrize("sql", [
    "INSERT INTO pecas (id, nome, preco, quantidade, estoque_minimo) VALUES ('p1', 'Filtro', 10, -1, 0)",
    "INSERT INTO servicos (id, nome, preco) VALUES ('s1', 'Revisão', 0)",
    "INSERT INTO itens_os (id, os_id, quantidade, preco_unitario) VALUES ('i1', 'o1', 1, 10)",
    "INSERT INTO itens_os (id, os_id, servico_id, peca_id, quantidade, preco_unitario) VALUES ('i2', 'o1', 's1', 'p1', 1, 10)",
    "INSERT INTO movimentacoes_estoque (id, peca_id, tipo, quantidade) VALUES ('m1', 'p1', 'AJUSTE', 1)",
], ids=["estoque negativo", "serviço sem preço", "item sem serviço nem peça", "item com serviço e peça", "movimentação desconhecida"])
def test_banco_recusa_dado_inconsistente(db, sql):
    with pytest.raises(IntegrityError):
        db.execute(text(sql))
