"""fix servico tempo_estimado_minutos type and unique names
Revision ID: b2c3d4e5f6a7 · Revises: a1b2c3d4e5f6"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "servicos",
        "tempo_estimado_minutos",
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="tempo_estimado_minutos::integer",
    )

    # Remove duplicados (mantém o menor ctid) antes de criar as constraints
    op.execute("""
        DELETE FROM servicos
        WHERE ctid NOT IN (
            SELECT min(ctid) FROM servicos GROUP BY lower(nome)
        )
    """)
    op.execute("""
        DELETE FROM pecas
        WHERE ctid NOT IN (
            SELECT min(ctid) FROM pecas GROUP BY lower(nome)
        )
    """)

    op.create_unique_constraint("uq_servicos_nome", "servicos", ["nome"])
    op.create_unique_constraint("uq_pecas_nome", "pecas", ["nome"])


def downgrade() -> None:
    op.drop_constraint("uq_pecas_nome", "pecas", type_="unique")
    op.drop_constraint("uq_servicos_nome", "servicos", type_="unique")
    op.alter_column(
        "servicos",
        "tempo_estimado_minutos",
        type_=sa.String(10),
        existing_nullable=True,
    )
