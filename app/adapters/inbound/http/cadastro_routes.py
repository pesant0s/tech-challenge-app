from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.security import get_current_user, require_admin
from app.adapters.outbound.persistence.cliente_repository import (
    ClienteRepositoryAdapter, VeiculoRepositoryAdapter,
)
from app.application.use_cases.gerenciar_cadastro import (
    GerenciarClientesUseCase, GerenciarVeiculosUseCase,
)
from app.adapters.inbound.http.cadastro_schemas import (
    ClienteCreate, ClienteUpdate, ClienteResponse, VeiculoCreate, VeiculoResponse,
)

router = APIRouter(prefix="/cadastro", tags=["👤 Clientes e Veículos"])


def _clientes_uc(db: Session) -> GerenciarClientesUseCase:
    return GerenciarClientesUseCase(ClienteRepositoryAdapter(db))


def _veiculos_uc(db: Session) -> GerenciarVeiculosUseCase:
    return GerenciarVeiculosUseCase(VeiculoRepositoryAdapter(db), ClienteRepositoryAdapter(db))


@router.post("/clientes", response_model=ClienteResponse, status_code=201,
    summary="Cadastrar cliente",
    description="Cria um novo cliente. CPF (11 dígitos) ou CNPJ (14 dígitos) obrigatório e único.")
def criar_cliente(data: ClienteCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return _clientes_uc(db).criar(data.model_dump())


@router.get("/clientes", response_model=list[ClienteResponse], summary="Listar clientes")
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return _clientes_uc(db).listar(skip=skip, limit=limit)


@router.get("/clientes/buscar", response_model=ClienteResponse,
    summary="Buscar por CPF/CNPJ",
    description="Identifica cliente pelo documento. Usado no início da criação da OS.")
def buscar_cliente_por_cpf(cpf_cnpj: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return _clientes_uc(db).buscar_por_documento(cpf_cnpj)


@router.get("/clientes/{cliente_id}", response_model=ClienteResponse,
    summary="Obter cliente por ID",
    description="**Requer ADMIN.**")
def obter_cliente(cliente_id: UUID, db: Session = Depends(get_db), _=Depends(require_admin)):
    return _clientes_uc(db).obter(cliente_id)


@router.patch("/clientes/{cliente_id}", response_model=ClienteResponse,
    summary="Atualizar cliente (parcial)",
    description="Atualiza nome, e-mail e/ou telefone. **CPF/CNPJ é imutável** — incluí-lo no body retorna 422.")
def atualizar_cliente(cliente_id: UUID, data: ClienteUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return _clientes_uc(db).atualizar(cliente_id, data.model_dump(exclude_unset=True))


@router.post("/veiculos", response_model=VeiculoResponse, status_code=201,
    summary="Cadastrar veículo",
    description="Cadastra veículo e vincula ao cliente. Placa deve ser formato AAA-1234 ou AAA1A23 (Mercosul).")
def criar_veiculo(data: VeiculoCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return _veiculos_uc(db).criar(data.model_dump())


@router.get("/clientes/{cliente_id}/veiculos", response_model=list[VeiculoResponse],
    summary="Listar veículos do cliente")
def listar_veiculos(cliente_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return _veiculos_uc(db).listar_por_cliente(cliente_id)


@router.get("/veiculos/{veiculo_id}", response_model=VeiculoResponse, summary="Obter veículo por ID")
def obter_veiculo(veiculo_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return _veiculos_uc(db).obter(veiculo_id)


@router.put("/veiculos/{veiculo_id}", response_model=VeiculoResponse, summary="Atualizar veículo")
def atualizar_veiculo(veiculo_id: UUID, data: VeiculoCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return _veiculos_uc(db).atualizar(veiculo_id, data.model_dump())


@router.delete("/veiculos/{veiculo_id}", status_code=204, summary="Remover veículo")
def deletar_veiculo(veiculo_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    _veiculos_uc(db).remover(veiculo_id)
