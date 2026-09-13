from sqlalchemy.orm import Session
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import ConflictException, NotFoundException
from app.infrastructure.security import pwd_context


def get_usuario_by_username(db: Session, username: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.username == username).first()


def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()


def create_usuario(db: Session, data) -> Usuario:
    if get_usuario_by_username(db, data.username):
        raise ConflictException(f"Username '{data.username}' já está em uso")
    u = Usuario(username=data.username, hashed_password=pwd_context.hash(data.password), role=data.role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def desativar_usuario(db: Session, usuario_id) -> Usuario:
    u = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not u:
        raise NotFoundException("Usuário não encontrado")
    u.ativo = False
    db.commit()
    db.refresh(u)
    return u
