"""add performance indexes
Revision ID: c3d4e5f6a7b8 · Revises: b2c3d4e5f6a7"""
from typing import Sequence, Union
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Filtragem de OS por status (rota GET /os?status=)
    op.create_index("ix_ordens_servico_status", "ordens_servico", ["status"])
    # Join OS → cliente (consulta pública por CPF/CNPJ)
    op.create_index("ix_ordens_servico_cliente_id", "ordens_servico", ["cliente_id"])
    # Join itens_os → OS
    op.create_index("ix_itens_os_os_id", "itens_os", ["os_id"])
    # Join veículos → cliente
    op.create_index("ix_veiculos_cliente_id", "veiculos", ["cliente_id"])
    # Movimentações → peça
    op.create_index("ix_movimentacoes_peca_id", "movimentacoes_estoque", ["peca_id"])


def downgrade() -> None:
    op.drop_index("ix_movimentacoes_peca_id", table_name="movimentacoes_estoque")
    op.drop_index("ix_veiculos_cliente_id", table_name="veiculos")
    op.drop_index("ix_itens_os_os_id", table_name="itens_os")
    op.drop_index("ix_ordens_servico_cliente_id", table_name="ordens_servico")
    op.drop_index("ix_ordens_servico_status", table_name="ordens_servico")
