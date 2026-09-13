import os
os.environ.setdefault("RATELIMIT_ENABLED", "False")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database import metadata, get_db

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    from app.domain.entities.usuario import RoleEnum
    from app.adapters.outbound.persistence.auth_repository import create_usuario
    from app.adapters.inbound.http.auth_schemas import UsuarioCreate
    create_usuario(db, UsuarioCreate(username="admin", password="admin123", role=RoleEnum.ADMIN))

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    """Token de ADMIN."""
    resp = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def atendente_headers(client, db):
    """Token de ATENDENTE."""
    from app.domain.entities.usuario import RoleEnum
    from app.adapters.outbound.persistence.auth_repository import create_usuario
    from app.adapters.inbound.http.auth_schemas import UsuarioCreate
    create_usuario(db, UsuarioCreate(username="atendente", password="atend123", role=RoleEnum.ATENDENTE))
    resp = client.post("/auth/token", data={"username": "atendente", "password": "atend123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def token_cliente():
    """Token no formato emitido pela Lambda; quebra aqui se a API deixar de aceitá-lo."""
    from datetime import datetime, timedelta, timezone
    from app.infrastructure.security import create_access_token

    def _emitir(cliente: dict, expira_em_minutos: int = 60, **sobrescrever) -> dict:
        claims = {
            "sub": cliente["id"],
            "tipo": "cliente",
            "cpf_cnpj": cliente["cpf_cnpj"],
            "nome": cliente["nome"],
            "iat": int(datetime.now(timezone.utc).timestamp()),
            **sobrescrever,
        }
        token = create_access_token(claims, expires_delta=timedelta(minutes=expira_em_minutos))
        return {"Authorization": f"Bearer {token}"}

    return _emitir
