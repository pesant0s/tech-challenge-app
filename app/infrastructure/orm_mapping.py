"""Mapeamento imperativo: as entidades de domínio seguem sem nenhum import de SQLAlchemy."""
import uuid
from datetime import timezone
from sqlalchemy import (
    Table, Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey,
    Enum, UniqueConstraint, TypeDecorator,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.infrastructure.database import mapper_registry, metadata
from app.domain.entities.usuario import Usuario, RoleEnum
from app.domain.entities.cliente import Cliente, Veiculo
from app.domain.entities.catalogo import Servico
from app.domain.entities.estoque import Peca, MovimentacaoEstoque
from app.domain.entities.os import OrdemDeServico, ItemOS, HistoricoStatusOS, StatusOS


class DataHoraUTC(TypeDecorator):
    """timestamptz sempre devolvido em UTC; o SQLite dos testes perde o fuso na leitura."""

    impl = DateTime
    cache_ok = True

    def process_result_value(self, valor, dialect):
        if valor is None:
            return None
        return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor.astimezone(timezone.utc)


usuarios = Table(
    "usuarios", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("username", String(50), unique=True, nullable=False, index=True),
    Column("hashed_password", String(255), nullable=False),
    Column("role", Enum(RoleEnum), nullable=False, default=RoleEnum.ATENDENTE),
    Column("ativo", Boolean, nullable=False, default=True),
)

clientes = Table(
    "clientes", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("nome", String(150), nullable=False),
    Column("cpf_cnpj", String(18), nullable=False, unique=True),
    Column("email", String(150), nullable=True),
    Column("telefone", String(20), nullable=False),
    Column("ativo", Boolean, nullable=False, default=True, server_default=text("true")),
)

veiculos = Table(
    "veiculos", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("placa", String(10), nullable=False, unique=True),
    Column("marca", String(60), nullable=False),
    Column("modelo", String(60), nullable=False),
    Column("ano", String(4), nullable=False),
    Column("cliente_id", UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True),
)

servicos = Table(
    "servicos", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("nome", String(150), nullable=False),
    Column("descricao", String(500), nullable=True),
    Column("preco", Numeric(10, 2), nullable=False),
    Column("tempo_estimado_minutos", Integer, nullable=True),
    UniqueConstraint("nome", name="uq_servicos_nome"),
)

pecas = Table(
    "pecas", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("nome", String(150), nullable=False),
    Column("descricao", String(500), nullable=True),
    Column("preco", Numeric(10, 2), nullable=False),
    Column("quantidade", Integer, nullable=False, default=0),
    Column("estoque_minimo", Integer, nullable=False, default=1),
    UniqueConstraint("nome", name="uq_pecas_nome"),
)

movimentacoes_estoque = Table(
    "movimentacoes_estoque", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("peca_id", UUID(as_uuid=True), ForeignKey("pecas.id"), nullable=False, index=True),
    Column("tipo", String(10), nullable=False),
    Column("quantidade", Integer, nullable=False),
    Column("motivo", String(200), nullable=True),
)

ordens_servico = Table(
    "ordens_servico", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("cliente_id", UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True),
    Column("veiculo_id", UUID(as_uuid=True), ForeignKey("veiculos.id"), nullable=False),
    Column("status", Enum(StatusOS), nullable=False, default=StatusOS.AGUARDANDO_APROVACAO, index=True),
    Column("valor_total", Numeric(10, 2), nullable=True),
    Column("criado_em", DataHoraUTC(timezone=True), server_default=func.now()),
    Column("iniciado_em", DataHoraUTC(timezone=True), nullable=True),
    Column("finalizado_em", DataHoraUTC(timezone=True), nullable=True),
)

itens_os = Table(
    "itens_os", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("os_id", UUID(as_uuid=True), ForeignKey("ordens_servico.id"), nullable=False, index=True),
    Column("servico_id", UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=True),
    Column("peca_id", UUID(as_uuid=True), ForeignKey("pecas.id"), nullable=True),
    Column("quantidade", Integer, nullable=False, default=1),
    Column("preco_unitario", Numeric(10, 2), nullable=False),
)

historico_status_os = Table(
    "historico_status_os", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("os_id", UUID(as_uuid=True), ForeignKey("ordens_servico.id"), nullable=False, index=True),
    Column("status", Enum(StatusOS), nullable=False),
    Column("entrou_em", DataHoraUTC(timezone=True), nullable=False),
)

mapper_registry.map_imperatively(Usuario, usuarios)
mapper_registry.map_imperatively(Servico, servicos)
mapper_registry.map_imperatively(Peca, pecas)
mapper_registry.map_imperatively(MovimentacaoEstoque, movimentacoes_estoque)

mapper_registry.map_imperatively(Cliente, clientes, properties={
    "veiculos": relationship(Veiculo, back_populates="cliente"),
})
mapper_registry.map_imperatively(Veiculo, veiculos, properties={
    "cliente": relationship(Cliente, back_populates="veiculos"),
})

mapper_registry.map_imperatively(HistoricoStatusOS, historico_status_os)
mapper_registry.map_imperatively(OrdemDeServico, ordens_servico, properties={
    "itens": relationship(ItemOS, back_populates="os", lazy="selectin"),
    "historico": relationship(HistoricoStatusOS, order_by=historico_status_os.c.entrou_em, lazy="selectin"),
})
mapper_registry.map_imperatively(ItemOS, itens_os, properties={
    "os": relationship(OrdemDeServico, back_populates="itens"),
})
