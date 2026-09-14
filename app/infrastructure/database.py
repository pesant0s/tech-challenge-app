from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker
from sqlalchemy.pool import QueuePool
from app.infrastructure.config import settings

mapper_registry = registry()
metadata = mapper_registry.metadata

# Até 5 conexões por processo: no teto do HPA (6 pods × 2 workers) são 60, dentro do limite do db.t4g.micro.
engine = create_engine(settings.DATABASE_URL, poolclass=QueuePool, pool_size=3, max_overflow=2, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# No fim do módulo: orm_mapping importa mapper_registry daqui.
from app.infrastructure import orm_mapping  # noqa: E402,F401
