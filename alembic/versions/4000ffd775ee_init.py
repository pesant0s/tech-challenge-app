"""init
Revision ID: 4000ffd775ee · Revises: 2bfe2db85dc4"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '4000ffd775ee'
down_revision: Union[str, None] = '2bfe2db85dc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
