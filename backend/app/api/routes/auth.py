from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import bearer_scheme, get_current_user
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    ResetPasswordRequest,
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


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    auth_service.request_password_reset(db, payload.email)
    # Resposta sempre igual: não revela se o e-mail está cadastrado (T-026).
    return MessageResponse(
        message=(
            "Se o e-mail estiver cadastrado, você receberá as "
            "instruções de redefinição."
        )
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    payload: ResetPasswordRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    auth_service.reset_password(db, payload.token, payload.password)
    return MessageResponse(message="Senha redefinida com sucesso.")
