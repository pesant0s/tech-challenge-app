"""adiciona status ao cliente, consultado pela Lambda de autenticação por CPF
Revision ID: d4e5f6a7b8c9 · Revises: c3d4e5f6a7b8"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default preenche as linhas que já existem.
    op.add_column("clientes", sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    op.drop_column("clientes", "ativo")
