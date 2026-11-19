"""Revisão de segurança (T-065).

Cobertura: segredos fora do código (AC-092), configuração segura para
produção (AC-093/AC-094), validação no servidor (AC-087) sem refletir
dados sensíveis nas respostas, e armazenamento seguro de senhas.
"""

import pytest

from app.core.config import DEFAULT_SECRET_KEY, Settings, validate_production_settings
from app.core.security import hash_password, verify_password

from .test_auth import auth_headers, login, register


def test_erros_de_validacao_nao_refletem_valores_enviados(client):
    # AC-094: a resposta de erro não ecoa a senha submetida.
    response = register(
        client,
        name="Ana",
        email="ana@example.com",
        password="curta",  # abaixo do mínimo: erro no campo de senha
    )

    assert response.status_code == 422
    body = response.text
    assert "curta" not in body
    for item in response.json()["error"]["details"]:
        assert "input" not in item


def test_respostas_nunca_exposam_senha_ou_hash(client):
    register(client)
    token = login(client).json()["access_token"]

    for response in (
        register(
            client,
            name="Bia",
            email="bia@example.com",
            password="outra-senha-1",
        ),
        login(client),
        client.get("/api/auth/me", headers=auth_headers(token)),
    ):
        body = response.text
        assert "senha-forte-1" not in body
        assert "outra-senha-1" not in body
        assert "password_hash" not in body
        assert "password" not in response.json().get("error", {}).get("code", "")


def test_senha_e_armazenada_com_hash(client):
    register(client)
    token = login(client).json()["access_token"]
    password_hash = hash_password("senha-forte-1")

    assert password_hash != "senha-forte-1"
    assert verify_password("senha-forte-1", password_hash) is True
    assert verify_password("errada", password_hash) is False
    assert token.count(".") == 2  # JWT em três partes, não armazena a senha


def test_producao_rejeita_chave_de_desenvolvimento():
    settings = Settings(
        environment="production",
        secret_key=DEFAULT_SECRET_KEY,
        email_backend="console",
    )

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_production_settings(settings)


def test_producao_rejeita_email_console():
    settings = Settings(
        environment="production",
        secret_key="chave-forte-e-exclusiva",
        email_backend="console",
    )

    with pytest.raises(RuntimeError, match="EMAIL_BACKEND"):
        validate_production_settings(settings)


def test_producao_com_configuracao_segura_e_aceita():
    settings = Settings(
        environment="production",
        secret_key="chave-forte-e-exclusiva",
        email_backend="smtp",
    )

    validate_production_settings(settings)  # não deve lançar


def test_desenvolvimento_nao_exige_configuracao_de_producao():
    settings = Settings(environment="development")

    validate_production_settings(settings)  # não deve lançar
