from sqlalchemy import select

from app.core.security import verify_password
from app.models import User

REGISTER = {
    "name": "Ana Silva",
    "email": "ana@example.com",
    "password": "senha-forte-1",
}


def register(client, **overrides):
    return client.post("/api/auth/register", json={**REGISTER, **overrides})


def login(client, email=REGISTER["email"], password=REGISTER["password"]):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_cria_usuario_sem_expor_senha(client):
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == REGISTER["email"]
    assert "password" not in body
    assert "password_hash" not in body


def test_register_rejeita_email_duplicado(client):
    register(client)
    response = register(client)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_already_registered"


def test_register_valida_campos(client):
    response = register(client, email="email-invalido", password="123")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_senha_armazenada_com_hash(client, db_session_factory):
    register(client)

    db = db_session_factory()
    user = db.scalar(select(User))
    assert user.password_hash.startswith("$2")
    assert verify_password(REGISTER["password"], user.password_hash)
    db.close()


def test_login_retorna_token_e_usuario(client):
    register(client)
    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == REGISTER["email"]


def test_login_com_senha_errada_retorna_mensagem_generica(client):
    register(client)
    response = login(client, password="senha-errada-1")

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "E-mail ou senha inválidos."


def test_login_com_email_inexistente_retorna_mesma_mensagem(client):
    response = login(client, email="ninguem@example.com", password="senha-errada-1")

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "E-mail ou senha inválidos."


def test_me_exige_autenticacao(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


def test_token_invalido_e_rejeitado(client):
    response = client.get("/api/auth/me", headers=auth_headers("token-invalido"))

    assert response.status_code == 401


def test_me_retorna_o_usuario_do_token(client):
    register(client)
    token = login(client).json()["access_token"]

    response = client.get("/api/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == REGISTER["email"]


def test_logout_invalida_a_sessao_imediatamente(client):
    register(client)
    token = login(client).json()["access_token"]
    headers = auth_headers(token)

    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_isolamento_entre_usuarios(client):
    """Cada token acessa apenas os próprios dados (T-025, AC-009)."""
    register(client)
    register(
        client,
        name="Bia Souza",
        email="bia@example.com",
        password="outra-senha-1",
    )
    token_ana = login(client).json()["access_token"]
    token_bia = login(client, email="bia@example.com", password="outra-senha-1").json()[
        "access_token"
    ]

    me_ana = client.get("/api/auth/me", headers=auth_headers(token_ana)).json()
    me_bia = client.get("/api/auth/me", headers=auth_headers(token_bia)).json()

    assert me_ana["email"] == "ana@example.com"
    assert me_bia["email"] == "bia@example.com"
    assert me_ana["id"] != me_bia["id"]
