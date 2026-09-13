from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.security import require_admin
from app.adapters.outbound.persistence import auth_repository as repo
from app.adapters.inbound.http.auth_schemas import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["🔐 Usuários"])


@router.post("/usuarios", response_model=UsuarioResponse, status_code=201,
    summary="Criar usuário",
    description="Cria um novo usuário com role ADMIN ou ATENDENTE. **Requer ADMIN.**")
def criar_usuario(data: UsuarioCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return repo.create_usuario(db, data)


@router.get("/usuarios", response_model=list[UsuarioResponse],
    summary="Listar usuários",
    description="**Requer ADMIN.**")
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return repo.get_usuarios(db, skip=skip, limit=limit)


@router.delete("/usuarios/{usuario_id}", response_model=UsuarioResponse,
    summary="Desativar usuário",
    description="Desativa o usuário (soft delete). **Requer ADMIN.**")
def desativar_usuario(usuario_id: UUID, db: Session = Depends(get_db), _=Depends(require_admin)):
    return repo.desativar_usuario(db, usuario_id)
