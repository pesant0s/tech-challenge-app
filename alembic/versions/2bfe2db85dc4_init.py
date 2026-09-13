"""init
Revision ID: 2bfe2db85dc4 · Revises: base"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2bfe2db85dc4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('clientes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('nome', sa.String(length=150), nullable=False),
    sa.Column('cpf_cnpj', sa.String(length=18), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=True),
    sa.Column('telefone', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cpf_cnpj')
    )
    op.create_table('pecas',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('nome', sa.String(length=150), nullable=False),
    sa.Column('descricao', sa.String(length=500), nullable=True),
    sa.Column('preco', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('quantidade', sa.Integer(), nullable=False),
    sa.Column('estoque_minimo', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('servicos',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('nome', sa.String(length=150), nullable=False),
    sa.Column('descricao', sa.String(length=500), nullable=True),
    sa.Column('preco', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('tempo_estimado_minutos', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movimentacoes_estoque',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('peca_id', sa.UUID(), nullable=False),
    sa.Column('tipo', sa.String(length=10), nullable=False),
    sa.Column('quantidade', sa.Integer(), nullable=False),
    sa.Column('motivo', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['peca_id'], ['pecas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('veiculos',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('placa', sa.String(length=10), nullable=False),
    sa.Column('marca', sa.String(length=60), nullable=False),
    sa.Column('modelo', sa.String(length=60), nullable=False),
    sa.Column('ano', sa.String(length=4), nullable=False),
    sa.Column('cliente_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('placa')
    )
    op.create_table('ordens_servico',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('cliente_id', sa.UUID(), nullable=False),
    sa.Column('veiculo_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('AGUARDANDO_APROVACAO', 'RECEBIDA', 'EM_DIAGNOSTICO', 'EM_EXECUCAO', 'FINALIZADA', 'ENTREGUE', 'NEGADA', 'ABANDONADA', name='statusos'), nullable=False),
    sa.Column('valor_total', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('iniciado_em', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finalizado_em', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
    sa.ForeignKeyConstraint(['veiculo_id'], ['veiculos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itens_os',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('os_id', sa.UUID(), nullable=False),
    sa.Column('servico_id', sa.UUID(), nullable=True),
    sa.Column('peca_id', sa.UUID(), nullable=True),
    sa.Column('quantidade', sa.Integer(), nullable=False),
    sa.Column('preco_unitario', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['os_id'], ['ordens_servico.id'], ),
    sa.ForeignKeyConstraint(['peca_id'], ['pecas.id'], ),
    sa.ForeignKeyConstraint(['servico_id'], ['servicos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('itens_os')
    op.drop_table('ordens_servico')
    op.drop_table('veiculos')
    op.drop_table('movimentacoes_estoque')
    op.drop_table('servicos')
    op.drop_table('pecas')
    op.drop_table('clientes')
    op.execute("DROP TYPE IF EXISTS statusos")
