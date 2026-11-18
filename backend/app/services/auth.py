"""Regras de autenticação: cadastro, login e sessão (T-022/T-023)."""

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import AuthSession, User
from app.schemas.auth import LoginRequest, UserCreate


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
        expires_at=datetime.now(UTC).replace(tzinfo=None)
        + timedelta(minutes=settings.access_token_expire_minutes),
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
