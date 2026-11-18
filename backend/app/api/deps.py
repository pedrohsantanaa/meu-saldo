from datetime import UTC, datetime, timedelta

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import AppError
from app.core.security import decode_access_token
from app.models import AuthSession, User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Retorna o usuário autenticado.

    Toda rota privada deve depender desta função: o usuário retornado é a
    única fonte de escopo dos dados (isolamento por usuário, T-025).
    """
    if credentials is None:
        raise AppError(
            code="unauthenticated",
            message="Autenticação necessária.",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    payload = decode_access_token(credentials.credentials)

    session = db.get(AuthSession, payload.get("sid", ""))
    if session is None or session.expires_at <= datetime.now(UTC).replace(tzinfo=None):
        raise AppError(
            code="invalid_token",
            message="Sessão inválida ou expirada. Faça login novamente.",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    user = db.get(User, int(payload.get("sub", 0)))
    if user is None:
        raise AppError(
            code="invalid_token",
            message="Sessão inválida ou expirada. Faça login novamente.",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    return user


def build_session_expiry() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
