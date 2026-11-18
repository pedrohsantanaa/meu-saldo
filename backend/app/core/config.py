from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração da aplicação carregada de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "meuSaldo API"
    environment: str = "development"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://meusaldo:meusaldo@localhost:5432/meusaldo"
    cors_origins: str = "http://localhost:5173"

    # Segurança (T-023): use uma chave forte em produção via variável SECRET_KEY.
    secret_key: str = "meusaldo-dev-secret-troque-em-producao"
    access_token_expire_minutes: int = 60

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
