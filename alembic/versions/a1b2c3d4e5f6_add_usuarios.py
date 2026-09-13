"""add usuarios table
Revision ID: a1b2c3d4e5f6 · Revises: 4000ffd775ee"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "4000ffd775ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "ATENDENTE", name="roleenum"),
            nullable=False,
            server_default="ATENDENTE",
        ),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_usuarios_username", "usuarios", ["username"])


def downgrade() -> None:
    op.drop_index("ix_usuarios_username", table_name="usuarios")
    op.drop_table("usuarios")
    op.execute("DROP TYPE IF EXISTS roleenum")
