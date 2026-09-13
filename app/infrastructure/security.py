import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.infrastructure.config import settings
from app.infrastructure.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dois esquemas para o mesmo cabeçalho: o Swagger oferece login de funcionário e token de cliente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
oauth2_opcional = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
bearer_cliente = HTTPBearer(scheme_name="TokenCliente", description="Token obtido em POST /auth/cpf", auto_error=False)

# Lambda e API assinam com a mesma SECRET_KEY; é o claim `tipo` que separa os dois públicos.
TIPO_CLIENTE = "cliente"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _credenciais_invalidas() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciais inválidas ou token expirado",
                         {"WWW-Authenticate": "Bearer"})


def _decodificar(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise _credenciais_invalidas()


def _usuario_do_payload(payload: dict, db: Session):
    if payload.get("tipo") == TIPO_CLIENTE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Token de cliente não dá acesso às rotas da oficina")
    from app.adapters.outbound.persistence.auth_repository import get_usuario_by_username
    user = get_usuario_by_username(db, payload.get("sub") or "")
    if user is None or not user.ativo:
        raise _credenciais_invalidas()
    return user


def _cliente_do_payload(payload: dict, db: Session):
    if payload.get("tipo") != TIPO_CLIENTE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Este endpoint exige token de cliente, obtido em POST /auth/cpf")
    try:
        cliente_id = uuid.UUID(str(payload.get("sub")))  # a coluna é UUID; texto cru quebraria o driver
    except ValueError:
        raise _credenciais_invalidas()
    from app.adapters.outbound.persistence.cliente_repository import ClienteRepositoryAdapter
    cliente = ClienteRepositoryAdapter(db).buscar_por_id(cliente_id)
    if cliente is None or not cliente.ativo:
        raise _credenciais_invalidas()
    return cliente


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return _usuario_do_payload(_decodificar(token), db)


def require_admin(current_user=Depends(get_current_user)):
    from app.domain.entities.usuario import RoleEnum
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a administradores")
    return current_user


def get_current_cliente(credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_cliente),
                        db: Session = Depends(get_db)):
    if credenciais is None:
        raise _credenciais_invalidas()
    return _cliente_do_payload(_decodificar(credenciais.credentials), db)


def get_escopo_cliente(token_funcionario: str | None = Depends(oauth2_opcional),
                       credenciais_cliente: HTTPAuthorizationCredentials | None = Depends(bearer_cliente),
                       db: Session = Depends(get_db)):
    """Aceita funcionário ou cliente; devolve o id do cliente, ou None para funcionário."""
    token = token_funcionario or (credenciais_cliente.credentials if credenciais_cliente else None)
    if not token:
        raise _credenciais_invalidas()
    payload = _decodificar(token)
    if payload.get("tipo") == TIPO_CLIENTE:
        return _cliente_do_payload(payload, db).id
    _usuario_do_payload(payload, db)
    return None
