"""histórico de status da OS, base do tempo médio por status
Revision ID: e5f6a7b8c9d0 · Revises: d4e5f6a7b8c9"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "historico_status_os",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("os_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ordens_servico.id"), nullable=False),
        sa.Column("status", postgresql.ENUM(name="statusos", create_type=False), nullable=False),
        sa.Column("entrou_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_historico_status_os_os_id", "historico_status_os", ["os_id"])
    # OS anteriores ao histórico entram com o status atual, a partir da criação.
    op.execute(
        "INSERT INTO historico_status_os (id, os_id, status, entrou_em) "
        "SELECT gen_random_uuid(), id, status, COALESCE(criado_em, now()) FROM ordens_servico"
    )


def downgrade() -> None:
    op.drop_index("ix_historico_status_os_os_id", table_name="historico_status_os")
    op.drop_table("historico_status_os")
