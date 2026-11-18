from datetime import UTC

from sqlalchemy import select

from app.models import PasswordResetToken

from .test_auth import REGISTER, auth_headers, login, register


def capture_email(monkeypatch):
    sent: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "app.services.auth.email_service.send_password_reset",
        lambda to, token: sent.append((to, token)),
    )
    return sent


def test_forgot_password_responde_igual_para_email_conhecido_ou_nao(
    client, monkeypatch
):
    sent = capture_email(monkeypatch)
    register(client)

    known = client.post("/api/auth/forgot-password", json={"email": REGISTER["email"]})
    unknown = client.post(
        "/api/auth/forgot-password", json={"email": "ninguem@example.com"}
    )

    assert known.status_code == unknown.status_code == 200
    # Resposta idêntica: não revela se o e-mail está cadastrado (T-026).
    assert known.json() == unknown.json()
    assert len(sent) == 1
    assert sent[0][0] == REGISTER["email"]


def test_reset_password_com_token_valido(client, monkeypatch):
    sent = capture_email(monkeypatch)
    register(client)
    client.post("/api/auth/forgot-password", json={"email": REGISTER["email"]})
    token = sent[0][1]

    response = client.post(
        "/api/auth/reset-password",
        json={"token": token, "password": "nova-senha-1"},
    )

    assert response.status_code == 200
    assert login(client, password=REGISTER["password"]).status_code == 401
    assert login(client, password="nova-senha-1").status_code == 200


def test_reset_password_revoga_as_sessoes_abertas(client, monkeypatch):
    sent = capture_email(monkeypatch)
    register(client)
    old_token = login(client).json()["access_token"]
    client.post("/api/auth/forgot-password", json={"email": REGISTER["email"]})

    client.post(
        "/api/auth/reset-password",
        json={"token": sent[0][1], "password": "nova-senha-1"},
    )

    me_response = client.get("/api/auth/me", headers=auth_headers(old_token))
    assert me_response.status_code == 401


def test_reset_token_e_de_uso_unico(client, monkeypatch):
    sent = capture_email(monkeypatch)
    register(client)
    client.post("/api/auth/forgot-password", json={"email": REGISTER["email"]})
    token = sent[0][1]

    first = client.post(
        "/api/auth/reset-password",
        json={"token": token, "password": "nova-senha-1"},
    )
    second = client.post(
        "/api/auth/reset-password",
        json={"token": token, "password": "outra-senha-1"},
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["error"]["code"] == "invalid_reset_token"


def test_reset_password_rejeita_token_invalido(client):
    response = client.post(
        "/api/auth/reset-password",
        json={"token": "token-inexistente", "password": "nova-senha-1"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_reset_token"


def test_reset_password_rejeita_token_expirado(client, monkeypatch, db_session_factory):
    from datetime import datetime, timedelta

    sent = capture_email(monkeypatch)
    register(client)
    client.post("/api/auth/forgot-password", json={"email": REGISTER["email"]})
    token = sent[0][1]

    db = db_session_factory()
    record = db.scalar(select(PasswordResetToken))
    record.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1)
    db.commit()
    db.close()

    response = client.post(
        "/api/auth/reset-password",
        json={"token": token, "password": "nova-senha-1"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_reset_token"


def test_banco_nao_armazena_o_token_em_texto_puro(
    client, monkeypatch, db_session_factory
):
    sent = capture_email(monkeypatch)
    register(client)
    client.post("/api/auth/forgot-password", json={"email": REGISTER["email"]})
    token = sent[0][1]

    db = db_session_factory()
    record = db.scalar(select(PasswordResetToken))
    assert record.id != token
    assert len(record.id) == 64
    db.close()
