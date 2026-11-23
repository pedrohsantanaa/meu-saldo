from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "meusaldo-dev-secret-troque-em-producao"


class Settings(BaseSettings):
    """Configuração da aplicação carregada de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Cifaro API"
    environment: str = "development"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://meusaldo:meusaldo@localhost:5432/meusaldo"
    cors_origins: str = "http://localhost:5173"

    # Segurança (T-023): use uma chave forte em produção via variável SECRET_KEY.
    secret_key: str = DEFAULT_SECRET_KEY
    access_token_expire_minutes: int = 60

    # Recuperação de senha (T-026).
    reset_token_expire_minutes: int = 30
    frontend_base_url: str = "http://localhost:5173"
    email_backend: str = "console"  # "console" (dev) ou "smtp" (produção)
    email_from: str = "no-reply@cifaro.com.br"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_production_settings(settings: Settings) -> None:
    """Endurecimento de produção (T-065, AC-092/AC-093/AC-094).

    Em produção a aplicação recusa iniciar com a chave de desenvolvimento
    ou com o backend de e-mail "console" (que registra links de recuperação
    de senha em log). HTTPS e CORS restrito são configurados na
    infraestrutura (T-068/T-069).
    """
    if settings.environment != "production":
        return

    problems = []
    if settings.secret_key == DEFAULT_SECRET_KEY:
        problems.append("SECRET_KEY ainda é o valor de desenvolvimento")
    if settings.email_backend == "console":
        problems.append('EMAIL_BACKEND="console" registra links de recuperação em log')
    if problems:
        raise RuntimeError(
            "Configuração insegura para produção: " + "; ".join(problems) + "."
        )


settings = get_settings()
