"""Regras de autenticação: cadastro, login, sessão e recuperação de senha."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import AuthSession, PasswordResetToken, User
from app.schemas.auth import LoginRequest, UserCreate
from app.services import email as email_service
from app.services.seed import seed_default_categories


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def register_user(db: Session, payload: UserCreate) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise AppError(
            code="email_already_registered",
            message="Este e-mail já está cadastrado.",
            http_status=409,
        )

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Categorias padrão do sistema como cópias do usuário (T-008).
    seed_default_categories(db, user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        # Mensagem genérica: não revela se o e-mail existe (AC-006).
        raise AppError(
            code="auth_failed",
            message="E-mail ou senha inválidos.",
            http_status=401,
        )
    return user


def create_session(db: Session, user: User) -> tuple[str, int]:
    session = AuthSession(
        id=secrets.token_hex(32),
        user_id=user.id,
        expires_at=_utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
    )
    db.add(session)
    db.commit()

    token, expires_in = create_access_token(user_id=user.id, session_id=session.id)
    return token, expires_in


def revoke_session(db: Session, session_id: str) -> None:
    session = db.get(AuthSession, session_id)
    if session is not None:
        db.delete(session)
        db.commit()


def revoke_all_sessions(db: Session, user_id: int) -> None:
    sessions = db.scalars(select(AuthSession).where(AuthSession.user_id == user_id))
    for session in sessions:
        db.delete(session)
    db.commit()


def request_password_reset(db: Session, email: str) -> None:
    """Prepara a redefinição de senha.

    Não revela se o e-mail está cadastrado: para e-mails desconhecidos,
    nenhuma ação é tomada e a rota responde sempre da mesma forma.
    """
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None:
        return

    # Token de uso único, com hash SHA-256 no banco (T-026).
    token = secrets.token_urlsafe(32)
    reset = PasswordResetToken(
        id=_hash_token(token),
        user_id=user.id,
        expires_at=_utcnow() + timedelta(minutes=settings.reset_token_expire_minutes),
    )
    db.add(reset)
    db.commit()

    email_service.send_password_reset(user.email, token)


def reset_password(db: Session, token: str, new_password: str) -> None:
    record = db.get(PasswordResetToken, _hash_token(token))
    if record is None or record.expires_at <= _utcnow():
        raise AppError(
            code="invalid_reset_token",
            message="O link de redefinição é inválido ou expirou.",
            http_status=400,
        )

    user = db.get(User, record.user_id)
    user.password_hash = hash_password(new_password)

    # Uso único + troca de senha encerra todas as sessões abertas.
    db.delete(record)
    db.commit()
    revoke_all_sessions(db, user.id)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
