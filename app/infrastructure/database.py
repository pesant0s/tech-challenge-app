from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker
from app.infrastructure.config import settings

mapper_registry = registry()
metadata = mapper_registry.metadata

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# No fim do módulo: orm_mapping importa mapper_registry daqui.
from app.infrastructure import orm_mapping  # noqa: E402,F401
