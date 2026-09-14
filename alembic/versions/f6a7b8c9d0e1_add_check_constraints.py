"""restrições CHECK para quantidades, preços, tipos de movimentação e itens de OS
Revision ID: f6a7b8c9d0e1 · Revises: e5f6a7b8c9d0"""
from typing import Sequence, Union

from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RESTRICOES = [
    ("servicos", "ck_servicos_preco_positivo", "preco > 0"),
    ("servicos", "ck_servicos_tempo_positivo", "tempo_estimado_minutos IS NULL OR tempo_estimado_minutos > 0"),
    ("pecas", "ck_pecas_preco_positivo", "preco > 0"),
    ("pecas", "ck_pecas_quantidade_nao_negativa", "quantidade >= 0"),
    ("pecas", "ck_pecas_estoque_minimo_nao_negativo", "estoque_minimo >= 0"),
    ("movimentacoes_estoque", "ck_movimentacoes_quantidade_positiva", "quantidade > 0"),
    ("movimentacoes_estoque", "ck_movimentacoes_tipo", "tipo IN ('ENTRADA', 'SAIDA')"),
    ("ordens_servico", "ck_ordens_servico_valor_nao_negativo", "valor_total IS NULL OR valor_total >= 0"),
    ("itens_os", "ck_itens_os_quantidade_positiva", "quantidade > 0"),
    ("itens_os", "ck_itens_os_preco_nao_negativo", "preco_unitario >= 0"),
    ("itens_os", "ck_itens_os_servico_ou_peca", "(servico_id IS NULL) <> (peca_id IS NULL)"),
]


def upgrade() -> None:
    for tabela, nome, condicao in RESTRICOES:
        op.create_check_constraint(nome, tabela, condicao)


def downgrade() -> None:
    for tabela, nome, _ in reversed(RESTRICOES):
        op.drop_constraint(nome, tabela, type_="check")
