from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import bearer_scheme, get_current_user
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    return auth_service.register_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.authenticate_user(db, payload)
    token, expires_in = auth_service.create_session(db, user)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserRead.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user: User = Depends(get_current_user),
    credentials=Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> MessageResponse:
    payload = decode_access_token(credentials.credentials)
    auth_service.revoke_session(db, payload["sid"])
    return MessageResponse(message="Sessão encerrada com sucesso.")


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
