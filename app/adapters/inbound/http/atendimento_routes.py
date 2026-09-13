from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.security import (
    get_current_cliente, get_current_user, get_escopo_cliente, require_admin,
)
from app.adapters.inbound.http.atendimento_schemas import OSCreate, OSResponse, OSStatusUpdate
from app.adapters.outbound.persistence.os_repository import OSRepositoryAdapter
from app.adapters.outbound.persistence.catalogo_repository import CatalogoRepositoryAdapter
from app.adapters.outbound.persistence.estoque_repository import EstoqueRepositoryAdapter
from app.adapters.outbound.persistence.cliente_repository import ClienteRepositoryAdapter
from app.adapters.outbound.notifications.email_simulado import EmailSimuladoAdapter
from app.application.use_cases.criar_os import CriarOSUseCase
from app.application.use_cases.listar_os import ListarOSUseCase
from app.application.use_cases.obter_os import ObterOSUseCase
from app.application.use_cases.atualizar_status import AtualizarStatusUseCase
from app.application.use_cases.aprovar_os import AprovarOSUseCase
from app.application.use_cases.rejeitar_os import RejeitarOSUseCase
from app.domain.entities.os import StatusOS

router = APIRouter(prefix="/atendimento", tags=["📋 Ordens de Serviço"])


@router.post("/os", response_model=OSResponse, status_code=201,
    summary="Criar Ordem de Serviço",
    description="Cria uma OS com status inicial **AGUARDANDO_APROVACAO**. O orçamento é calculado automaticamente.")
def criar_os(data: OSCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return CriarOSUseCase(
        os_repo=OSRepositoryAdapter(db),
        catalogo_repo=CatalogoRepositoryAdapter(db),
        estoque_repo=EstoqueRepositoryAdapter(db),
        cliente_repo=ClienteRepositoryAdapter(db),
        notificador=EmailSimuladoAdapter(),
    ).executar(data.cliente_id, data.veiculo_id, data.servicos, data.pecas)


@router.get("/os", response_model=list[OSResponse], summary="Listar todas as OS")
def listar_os(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: StatusOS | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return ListarOSUseCase(OSRepositoryAdapter(db)).executar(skip, limit, status)


@router.get("/os/metricas/tempo-medio",
    summary="Tempo médio de execução",
    description="Retorna o tempo médio (em minutos) entre início e finalização. **Requer ADMIN.**")
def tempo_medio(db: Session = Depends(get_db), _=Depends(require_admin)):
    return OSRepositoryAdapter(db).tempo_medio_execucao()


@router.get("/os/consulta", response_model=list[OSResponse],
    summary="Minhas ordens de serviço (cliente)",
    description="""
Requer **token de cliente**, obtido em `POST /auth/cpf`. Devolve apenas as ordens de
serviço de quem está autenticado — o CPF vem do token, não da requisição, então não
há como consultar as ordens de outra pessoa.
""")
def consultar_minhas_os(db: Session = Depends(get_db), cliente=Depends(get_current_cliente)):
    return OSRepositoryAdapter(db).buscar_por_cliente_id(cliente.id)


@router.get("/os/fila", response_model=list[OSResponse],
    summary="Fila de OS por prioridade operacional",
    description="""
Retorna as OS **ativas** ordenadas por prioridade:

| Prioridade | Status |
|---|---|
| 1 | EM_EXECUCAO |
| 2 | AGUARDANDO_APROVACAO |
| 3 | EM_DIAGNOSTICO |
| 4 | RECEBIDA |

`FINALIZADA` e `ENTREGUE` são excluídas. Dentro de cada prioridade, a mais antiga aparece primeiro.
""")
def listar_fila(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return OSRepositoryAdapter(db).listar_fila_priorizada()


@router.get("/os/{os_id}", response_model=OSResponse,
    summary="Consultar OS por ID",
    description="""
Aceita **token de funcionário ou de cliente**. Funcionário consulta qualquer OS; cliente,
apenas as próprias. A OS de outro cliente responde `404`, idêntico a uma OS inexistente.
""")
def obter_os(os_id: UUID, db: Session = Depends(get_db), cliente_id=Depends(get_escopo_cliente)):
    return ObterOSUseCase(OSRepositoryAdapter(db)).executar(os_id, cliente_id=cliente_id)


@router.post("/os/{os_id}/aprovar", response_model=OSResponse,
    summary="Aprovar orçamento (cliente)",
    description="Requer **token de cliente**. Move a OS de `AGUARDANDO_APROVACAO` → `RECEBIDA`. Só o titular da OS consegue aprovar.")
def aprovar_os(os_id: UUID, db: Session = Depends(get_db), cliente=Depends(get_current_cliente)):
    # O CPF sai do token; o caso de uso ainda confere a titularidade, como no webhook.
    return AprovarOSUseCase(
        os_repo=OSRepositoryAdapter(db),
        cliente_repo=ClienteRepositoryAdapter(db),
    ).executar(os_id, cliente.cpf_cnpj)


@router.post("/os/{os_id}/rejeitar", response_model=OSResponse,
    summary="Rejeitar orçamento (cliente)",
    description="Requer **token de cliente**. Move a OS de `AGUARDANDO_APROVACAO` → `NEGADA`. Só o titular da OS consegue rejeitar.")
def rejeitar_os(os_id: UUID, db: Session = Depends(get_db), cliente=Depends(get_current_cliente)):
    return RejeitarOSUseCase(
        os_repo=OSRepositoryAdapter(db),
        cliente_repo=ClienteRepositoryAdapter(db),
    ).executar(os_id, cliente.cpf_cnpj)


@router.patch("/os/{os_id}/status", response_model=OSResponse,
    summary="Atualizar status da OS",
    description="""
Transições válidas:

| De | Para |
|---|---|
| AGUARDANDO_APROVACAO | RECEBIDA, NEGADA, ABANDONADA |
| RECEBIDA | EM_DIAGNOSTICO |
| EM_DIAGNOSTICO | AGUARDANDO_APROVACAO, EM_EXECUCAO |
| EM_EXECUCAO | FINALIZADA |
| FINALIZADA | ENTREGUE |

Ao mover para **EM_EXECUCAO**, as peças vinculadas são baixadas automaticamente do estoque.
""")
def atualizar_status(
    os_id: UUID,
    data: OSStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return AtualizarStatusUseCase(
        os_repo=OSRepositoryAdapter(db),
        estoque_repo=EstoqueRepositoryAdapter(db),
    ).executar(os_id, data.status)
